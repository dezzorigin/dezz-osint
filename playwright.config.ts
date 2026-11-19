import { defineConfig, devices } from "@playwright/test";

// Landing dezz-osint adalah etalase statis: yang diuji adalah konten +
// interaksi halamannya (tab terminal, tombol salin, tabel mesin).
// CLI-nya sendiri diuji di job pytest CI — bukan di browser,
// karena CLI butuh terminal + jaringan ke sumber OSINT.
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 0,
  use: { baseURL: "http://127.0.0.1:8395" },
  webServer: {
    command: "python3 -m http.server 8395 --bind 127.0.0.1",
    url: "http://127.0.0.1:8395/",
    reuseExistingServer: true,
    timeout: 15_000,
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "mobile", use: { ...devices["Pixel 7"], viewport: { width: 390, height: 844 } } },
  ],
});
