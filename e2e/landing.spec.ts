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
  // DIAG SEMENTARA (hapus sesudah diagnosis): laporkan elemen yang
  // melebar melewati viewport + gaya terhitung yang menentukan.
  const diag = await page.evaluate(() => {
    const q = (s: string) => document.querySelector(s) as HTMLElement | null;
    const lines: string[] = [];
    lines.push(`doc scrollWidth=${document.documentElement.scrollWidth} clientWidth=${document.documentElement.clientWidth}`);
    for (const s of [".dossier", ".rail", ".content", ".terminal", ".engines", ".install-card", ".foot", ".topbar"]) {
      const el = q(s);
      if (el) lines.push(`${s}: w=${Math.round(el.getBoundingClientRect().width)} scrollW=${el.scrollWidth} clientW=${el.clientWidth} display=${getComputedStyle(el).display}`);
    }
    lines.push(`dossier gridTemplateColumns=${getComputedStyle(q(".dossier")!).gridTemplateColumns}`);
    lines.push(`engines display=${getComputedStyle(q(".engines")!).display} thead=${getComputedStyle(q(".engines thead")!).display}`);
    lines.push(`install pre scrollW=${(q(".install-card pre") as HTMLElement)?.scrollWidth} clientW=${(q(".install-card pre") as HTMLElement)?.clientWidth}`);
    const vw = document.documentElement.clientWidth;
    const out: string[] = [];
    document.querySelectorAll("body *").forEach((el) => {
      const r = (el as HTMLElement).getBoundingClientRect();
      if (r.right <= vw + 1) return;
      let p: HTMLElement | null = (el as HTMLElement).parentElement;
      let clipped = false;
      while (p && p !== document.body) {
        const o = getComputedStyle(p).overflowX;
        if (o === "auto" || o === "hidden" || o === "scroll") { clipped = true; break; }
        p = p.parentElement;
      }
      if (clipped) return;
      const cls = typeof el.className === "string" ? el.className.split(" ")[0] : "";
      out.push(`${el.tagName.toLowerCase()}${cls ? "." + cls : ""} w=${Math.round(r.width)} right=${Math.round(r.right)} :: ${(el.textContent || "").trim().slice(0, 60)}`);
    });
    lines.push("OFFENDERS:\n" + (out.slice(0, 30).join("\n") || "(tidak ada)"));
    return lines.join("\n");
  });
  console.log("DIAG-OVERFLOW:\n" + diag);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  await expect(page.locator("h1").first()).toBeVisible();
  await expect(page.locator(".engines tbody tr").first()).toBeVisible();
});
