/** One-line restart from repo root (PowerShell). */
export const UVICORN_RESTART_LINE =
  "uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705";

/** Starts FastAPI + Vite for local dev (run inside repo root). */
export const WEBAPP_START_FROM_ROOT = "Set-Location webapp; .\\start.ps1";

export async function copyRecoveryCommand(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
