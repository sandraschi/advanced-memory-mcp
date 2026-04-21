import { expect, test } from "@playwright/test";

test.describe("webapp smoke", () => {
  test("home dashboard renders hero", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Notes, research, and retrieval" }),
    ).toBeVisible({ timeout: 30_000 });
  });

  test("note vault shows project picker and search", async ({ page }) => {
    await page.goto("/notes");
    await expect(page.getByLabel("Project")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByPlaceholder("Search notes... (press Enter)")).toBeVisible();
    await expect(page.getByRole("link", { name: "Sync and index" })).toBeVisible();
  });

  test("vault sync page loads", async ({ page }) => {
    await page.goto("/vault/sync");
    await expect(page.getByRole("heading", { name: "Vault sync" })).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByRole("heading", { name: "Target project" })).toBeVisible();
  });

  test("FastAPI health responds", async ({ request }) => {
    const res = await request.get("http://127.0.0.1:10705/api/v1/health");
    expect(res.ok()).toBeTruthy();
  });
});
