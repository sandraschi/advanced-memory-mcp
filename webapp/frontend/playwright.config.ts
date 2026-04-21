import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
/** Repo root (contains `pyproject.toml`, `src/advanced_memory`). */
const repoRoot = path.resolve(__dirname, "../..");

/** True only on GitHub Actions — avoid treating a local `CI=1` as “must spawn servers”. */
const isGithubActions = Boolean(process.env.GITHUB_ACTIONS);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: isGithubActions,
  retries: isGithubActions ? 1 : 0,
  workers: isGithubActions ? 1 : 4,
  reporter: isGithubActions ? "github" : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:10704",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705",
      cwd: repoRoot,
      url: "http://127.0.0.1:10705/api/v1/health",
      reuseExistingServer: !isGithubActions,
      timeout: 180_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      command: "npm run dev",
      cwd: __dirname,
      url: "http://127.0.0.1:10704/",
      reuseExistingServer: !isGithubActions,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],
});
