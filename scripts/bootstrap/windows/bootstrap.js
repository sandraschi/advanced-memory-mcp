#!/usr/bin/env node
/* eslint-disable no-console */

/**
 * Windows bootstrapper for Advanced Memory MCP.
 *
 * Usage (local, via npx):
 *   npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- --target D:\Dev\repos
 *
 * The script clones the repository, runs uv sync, and prints final setup guidance.
 */

const { spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const REPO_URL = "https://github.com/sandraschi/advanced-memory-mcp.git";

function exitWithError(message) {
  console.error(`\n[ERROR] ${message}`);
  process.exit(1);
}

function info(message) {
  console.log(`[INFO] ${message}`);
}

function success(message) {
  console.log(`[OK] ${message}`);
}

function warn(message) {
  console.warn(`[WARN] ${message}`);
}

function ensureWindows() {
  if (process.platform !== "win32") {
    exitWithError("This bootstrapper currently supports Windows only.");
  }
}

function ensureNodeVersion() {
  const [major] = process.versions.node.split(".").map(Number);
  if (Number.isNaN(major) || major < 18) {
    exitWithError("Node.js 18 or newer is required.");
  }
}

function commandExists(cmd) {
  const lookup = spawnSync("where", [cmd], { stdio: "ignore", shell: true });
  return lookup.status === 0;
}

function assertDependency(command, installHint) {
  if (!commandExists(command)) {
    exitWithError(
      `${command} is required but was not found on PATH.\n` +
        `Install hint: ${installHint}`,
    );
  }
}

function run(command, args, options = {}) {
  info(`Running: ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: true,
    ...options,
  });
  if (result.status !== 0) {
    exitWithError(`Command failed: ${command} ${args.join(" ")}`);
  }
}

function runOptional(command, args, options = {}) {
  info(`Running (optional): ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: true,
    ...options,
  });
  if (result.status !== 0) {
    warn(
      `Optional command failed (${command} ${args.join(
        " ",
      )}). Continuing bootstrap.`,
    );
    return false;
  }
  return true;
}

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "--target" && args[i + 1]) {
      parsed.target = args[i + 1];
      i += 1;
    } else if (arg === "--generate-configs") {
      parsed.generateConfigs = true;
    } else if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else {
      warn(`Unknown argument: ${arg}`);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`
Advanced Memory MCP Windows Bootstrapper
----------------------------------------
Usage:
  npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- [options]

Options:
  --target <path>   Base directory where the repository will be cloned.
                    Default: D:\\Dev\\repos if drive D exists, otherwise C:\\Dev\\repos
  --generate-configs  Emit MCP config templates for Cursor, Windsurf, and Claude Desktop.
  --help              Show this message.

Example:
  npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- --target D:\\Dev\\repos
`);
}

function determineTargetDir(targetArg) {
  if (targetArg) {
    return path.resolve(expandPath(targetArg));
  }
  const preferredDrive = fs.existsSync("D:\\") ? "D:" : "C:";
  return path.join(preferredDrive, "Dev", "repos");
}

function ensureDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    success(`Created directory: ${dirPath}`);
  }
}

function cloneOrUpdateRepo(baseDir) {
  const repoDir = path.join(baseDir, "advanced-memory-mcp");
  if (fs.existsSync(path.join(repoDir, ".git"))) {
    info("Repository already exists. Pulling latest changes.");
    run("git", ["-C", repoDir, "fetch", "--all"]);
    run("git", ["-C", repoDir, "pull", "--ff-only"]);
  } else {
    info(`Cloning into ${repoDir}`);
    run("git", ["clone", REPO_URL, repoDir]);
  }
  return repoDir;
}

function runUvSync(repoDir) {
  run("uv", ["sync"], { cwd: repoDir });
}

function runSmokeChecks(repoDir) {
  run("uv", ["run", "ruff", "check", "."], { cwd: repoDir });
  runOptional("uv", ["run", "python", "-m", "advanced_memory.services.skill_creator.cli", "validate", "skills/advanced-memory/advanced-memory-skill-creator"], {
    cwd: repoDir,
  });
}

function expandPath(inputPath) {
  if (!inputPath) {
    return inputPath;
  }
  let expanded = inputPath;
  expanded = expanded.replace(/%([^%]+)%/g, (match, name) => {
    const value = process.env[name];
    return value !== undefined ? value : match;
  });
  if (expanded.startsWith("~")) {
    expanded = path.join(os.homedir(), expanded.slice(1));
  }
  return expanded;
}

function writeConfigTemplates(repoDir, advancedMemoryHome) {
  const configDir = path.join(repoDir, "bootstrap-configs");
  ensureDirectory(configDir);

  const baseConfig = {
    mcpServers: {
      "advanced-memory": {
        command: "uv",
        args: ["run", "python", "-m", "advanced_memory.mcp.server"],
        env: {
          ADVANCED_MEMORY_HOME: advancedMemoryHome,
          ADVANCED_MEMORY_PORTMANTEAU_ONLY: "true",
        },
      },
    },
  };

  const cursorPath = path.join(configDir, "cursor-mcp.config.json");
  fs.writeFileSync(cursorPath, `${JSON.stringify(baseConfig, null, 2)}\n`, {
    encoding: "utf-8",
  });

  const windsufPath = path.join(configDir, "windsurf-mcp.config.json");
  fs.writeFileSync(windsufPath, `${JSON.stringify(baseConfig, null, 2)}\n`, {
    encoding: "utf-8",
  });

  const claudeConfig = {
    ...baseConfig,
  };
  const claudePath = path.join(configDir, "claude-desktop-mcp.config.json");
  fs.writeFileSync(claudePath, `${JSON.stringify(claudeConfig, null, 2)}\n`, {
    encoding: "utf-8",
  });

  success(`Wrote MCP config templates to ${configDir}`);
  return { configDir, cursorPath, windsufPath, claudePath };
}

function printCompletion(repoDir, configInfo) {
  const claudeConfig = path.join(
    os.homedir(),
    "AppData",
    "Roaming",
    "Claude",
    "claude_desktop_config.json",
  );
  console.log(`
========================================
Advanced Memory MCP setup complete!
Repository: ${repoDir}

Next steps:
 1. Point Cursor/Windsurf at the repository:
    ${repoDir}
 2. For Claude Desktop (manual install):
    - Add configuration to claude_desktop_config.json:
        {
          "mcpServers": {
            "advanced-memory": {
              "command": "uv",
              "args": ["run", "python", "-m", "advanced_memory.mcp.server"],
              "env": {
                "ADVANCED_MEMORY_HOME": "${path.join(
                  os.homedir(),
                  ".advanced-memory",
                )}"
              }
            }
          }
        }
    - File location: ${claudeConfig}
 3. Review README.md for integration details.
${configInfo ? `4. Config templates ready in: ${configInfo.configDir}` : ""}

If you plan to package this bootstrapper on npm later, reuse this script.
========================================
`);
}

function main() {
  ensureWindows();
  ensureNodeVersion();

  const parsed = parseArgs();
  if (parsed.help) {
    printHelp();
    return;
  }

  assertDependency("git", "Install Git for Windows: https://git-scm.com/download/win");
  assertDependency(
    "python",
    "Install Python 3.11+ for Windows and ensure 'Add python.exe to PATH' is checked.",
  );
  assertDependency(
    "uv",
    "Install uv by running: powershell -ExecutionPolicy Bypass -c \"iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex\"",
  );

  const targetBase = determineTargetDir(parsed.target);
  ensureDirectory(targetBase);

  const repoDir = cloneOrUpdateRepo(targetBase);

  runUvSync(repoDir);
  runSmokeChecks(repoDir);
  let configInfo;
  const advancedMemoryHome = path.join(os.homedir(), ".advanced-memory");
  if (parsed.generateConfigs) {
    configInfo = writeConfigTemplates(repoDir, advancedMemoryHome);
  }
  printCompletion(repoDir, configInfo);
}

main();

