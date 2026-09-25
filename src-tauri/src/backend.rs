use std::fs::{self, OpenOptions};
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpStream, ToSocketAddrs};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

use tauri::path::BaseDirectory;
use tauri::{AppHandle, Emitter, Manager};

pub struct BackendProcess(pub Mutex<Option<Child>>);

// -- PER-REPO: Customize these constants --
const BACKEND_NAME: &str = "advanced-memory-mcp-backend.exe";
const BACKEND_PORT: u16 = 10705;
const BACKEND_TAG: &str = "advanced-memory-mcp-backend-x86_64-pc-windows-msvc.exe";
const ENV_PORT: &str = "ADVANCED_MEMORY_MCP_PORT";
const ENV_HOST: &str = "ADVANCED_MEMORY_MCP_HOST";
const ENV_TAURI: &str = "ADVANCED_MEMORY_MCP_TAURI";

fn dev_backend_path() -> Option<PathBuf> {
    if !cfg!(debug_assertions) {
        return None;
    }
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("binaries")
        .join(BACKEND_TAG);
    path.exists().then_some(path)
}

fn log_line(app: &AppHandle, message: &str) {
    eprintln!("[backend] {message}");
    if let Ok(dir) = app.path().app_log_dir() {
        let _ = fs::create_dir_all(&dir);
        let log_path = dir.join("backend-spawn.log");
        if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(log_path) {
            let _ = writeln!(file, "{message}");
        }
    }
}

fn resolve_bundled_backend(app: &AppHandle) -> Result<PathBuf, String> {
    let mut tried = Vec::new();

    if let Ok(path) = app.path().resolve(BACKEND_NAME, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() {
            return Ok(path);
        }
    }

    let resources_path = format!("resources/{BACKEND_NAME}");
    if let Ok(path) = app.path().resolve(&resources_path, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() {
            return Ok(path);
        }
    }

    if let Ok(dir) = app.path().executable_dir() {
        let path = dir.join("resources").join(BACKEND_NAME);
        tried.push(path.display().to_string());
        if path.exists() {
            return Ok(path);
        }
    }

    Err(format!("bundled backend missing from resources (tried: {})", tried.join("; ")))
}

fn install_dir_from_backend(path: &PathBuf) -> PathBuf {
    if let Some(parent) = path.parent() {
        if parent
            .file_name()
            .is_some_and(|name| name.eq_ignore_ascii_case("resources"))
        {
            if let Some(install_dir) = parent.parent() {
                return install_dir.to_path_buf();
            }
        }
        return parent.to_path_buf();
    }
    PathBuf::from(".")
}

pub fn materialize_backend(app: &AppHandle) -> Result<PathBuf, String> {
    if let Some(dev_path) = dev_backend_path() {
        log_line(app, &format!("using dev backend: {}", dev_path.display()));
        return Ok(dev_path);
    }

    let bundled = resolve_bundled_backend(app)?;
    log_line(app, &format!("using bundled backend: {}", bundled.display()));
    Ok(bundled)
}

/// True if something on 127.0.0.1:port is not just bound but actually
/// answering HTTP requests - i.e. a live, healthy backend, not a zombie
/// that crashed mid-request and left the port bound with nothing behind it.
///
/// A bare TCP connect isn't enough to justify skipping the kill+spawn below:
/// a hung or crashing process can still hold the port open while answering
/// nothing. So this sends a minimal HTTP request and only counts the port
/// as "already serving" if *any* HTTP response comes back within the
/// timeout - the exact status code and path don't matter (every repo's
/// health route differs), only that something is genuinely alive and
/// speaking HTTP. Force-killing is still the right move for a port held by
/// a truly unresponsive process; this only protects a *healthy* holder
/// (almost always the NSSM-managed service) from being killed just for
/// existing, which was the actual bug in free_port below.
fn port_holder_is_responsive(port: u16) -> bool {
    let addr = match ("127.0.0.1", port).to_socket_addrs() {
        Ok(mut addrs) => match addrs.next() {
            Some(addr) => addr,
            None => return false,
        },
        Err(_) => return false,
    };
    let mut stream = match TcpStream::connect_timeout(&addr, Duration::from_millis(500)) {
        Ok(s) => s,
        Err(_) => return false, // nothing listening at all
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(1500)));
    let _ = stream.set_write_timeout(Some(Duration::from_millis(500)));
    let request = format!("GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n\r\n");
    if stream.write_all(request.as_bytes()).is_err() {
        return false; // connected but can't even send - treat as a zombie
    }
    let mut buf = [0u8; 16];
    matches!(stream.read(&mut buf), Ok(n) if n > 0 && buf[..n].starts_with(b"HTTP/"))
}

fn free_port(port: u16) {
    #[cfg(windows)]
    {
        let script = format!("Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ taskkill /F /PID `$_.OwningProcess /T 2>$null }}");
        let _ = Command::new("powershell.exe")
            .args(["-NoProfile", "-Command", &script])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
        thread::sleep(Duration::from_millis(300));
    }
}

fn stop_managed_child(state: &BackendProcess) {
    if let Some(mut child) = state.0.lock().unwrap().take() {
        let _ = child.kill();
        let _ = child.wait();
    }
}

pub fn spawn_backend(app: AppHandle, state: &BackendProcess) -> Result<String, String> {
    stop_managed_child(state);

    // If something healthy is already serving on BACKEND_PORT - almost
    // always the NSSM-managed advanced-memory-mcp service, which every
    // other MCP client (stdio proxies, the webapp) depends on staying up -
    // attach to it instead of force-killing it and spawning a redundant
    // second backend over the same shared vault/db. A genuinely dead/hung
    // holder still gets force-killed below, same as before. state.0 is left
    // None when we attach, so the RunEvent::Exit handler in main.rs
    // correctly does NOT kill a backend this Tauri instance never spawned.
    if port_holder_is_responsive(BACKEND_PORT) {
        log_line(
            &app,
            &format!(
                "port {BACKEND_PORT} already serving - attaching to existing backend instead of spawning a second one"
            ),
        );
        return Ok(format!("Attached to existing backend on port {BACKEND_PORT}"));
    }

    free_port(BACKEND_PORT);

    let backend_path = materialize_backend(&app)?;
    let workdir = app
        .path()
        .executable_dir()
        .ok()
        .unwrap_or_else(|| install_dir_from_backend(&backend_path));

    log_line(
        &app,
        &format!("spawning {} (cwd {}) on port {BACKEND_PORT}",
            backend_path.display(), workdir.display()),
    );

    let mut command = Command::new(&backend_path);
    command
        .current_dir(&workdir)
        .env(ENV_PORT, BACKEND_PORT.to_string())
        .env(ENV_HOST, "127.0.0.1")
        .env(ENV_TAURI, "1")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        command.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = command
        .spawn()
        .map_err(|e| format!("Failed to spawn {}: {e}", backend_path.display()))?;

    let stdout = child.stdout.take();
    let stderr = child.stderr.take();
    state.0.lock().unwrap().replace(child);

    if let Some(out) = stdout {
        let app_handle = app.clone();
        thread::spawn(move || watch_backend_stream(out, app_handle));
    }
    if let Some(err) = stderr {
        let app_handle = app.clone();
        thread::spawn(move || watch_backend_stream(err, app_handle));
    }

    Ok(format!("Backend starting on port {BACKEND_PORT}"))
}

fn watch_backend_stream<R: std::io::Read + Send + 'static>(stream: R, app: AppHandle) {
    let reader = BufReader::new(stream);
    let mut ready = false;
    for line in reader.lines().map_while(Result::ok) {
        log_line(&app, &line);
        if !ready
            && (line.contains("Uvicorn running") || line.contains("Application startup complete"))
        {
            ready = true;
            let _ = app.emit("backend-status", "ready");
        }
    }
}

