import { test, expect } from "@playwright/test";

// Landing dezz-osint adalah etalase CLI + MCP: yang diuji adalah konten
// + interaksi halamannya (tab terminal, tombol salin, tabel mesin, cap
// verdict). CLI-nya sendiri diuji di job pytest CI (perilaku live).

test("landing tampil: judul, terminal, tabel 14 mesin, MCP 13 tool", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/dezz-osint/i);
  await expect(page.locator("text=Satu target,").first()).toBeVisible();
  await expect(page.locator("text=Jendela terminal").first()).toBeVisible();
  await expect(page.locator("text=Empat belas mesin").first()).toBeVisible();
  await expect(page.locator(".engines tbody tr")).toHaveCount(14);
  await expect(page.locator(".tool-chips li")).toHaveCount(13);
  // kejujuran isi: ini etalase, bukan pengganti CLI
  await expect(page.locator("text=etalase").first()).toBeVisible();
  // cap verdict tampil
  await expect(page.locator("text=[verified]").first()).toBeVisible();
  await expect(page.locator("text=[SKIP]").first()).toBeVisible();
  // angka nyata repo
  await expect(page.locator("text=3.793").first()).toBeVisible();
  await expect(page.locator("text=233").first()).toBeVisible();
});

test("tab terminal berganti output", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#term-ip")).toBeVisible();
  await expect(page.locator("#term-ip")).toContainText("Ashburn");
  await page.getByRole("tab", { name: "dezz github torvalds" }).click();
  await expect(page.locator("#term-github")).toBeVisible();
  await expect(page.locator("#term-github")).toContainText("Linus Torvalds");
  await expect(page.locator("#term-ip")).toBeHidden();
  await page.getByRole("tab", { name: /sherlock/ }).click();
  await expect(page.locator("#term-resources")).toContainText("SherlockEye");
});

test("mobile 390px: tanpa scroll horizontal", async ({ page }) => {
  await page.goto("/");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  await expect(page.locator("h1").first()).toBeVisible();
  await expect(page.locator(".engines tbody tr").first()).toBeVisible();
});
