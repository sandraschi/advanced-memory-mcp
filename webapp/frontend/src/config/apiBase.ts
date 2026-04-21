/**
 * Base URL for the Advanced Memory HTTP API (FastAPI / uvicorn).
 * - Dev: default `/api/v1` so Vite proxies to the backend (see vite.config.ts).
 * - Docker / custom host: set VITE_API_URL (e.g. http://backend:10705/api/v1).
 */
export function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_URL?.trim();
  if (fromEnv) {
    return fromEnv.replace(/\/$/, "");
  }
  return "/api/v1";
}
