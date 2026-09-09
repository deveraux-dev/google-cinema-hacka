const { test, expect } = require("@playwright/test");
const baseUrl = process.env.BASE_URL || "http://127.0.0.1:8000";

if (process.env.PLAYWRIGHT_CHROME_PATH) {
  test.use({
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROME_PATH,
    },
  });
}

for (const viewport of [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 900 },
]) {
  test(`HUD renders and analyzes on ${viewport.name}`, async ({ page }) => {
    const consoleProblems = [];
    page.on("console", (msg) => {
      if (["error", "warning"].includes(msg.type())) {
        consoleProblems.push(`${msg.type()}: ${msg.text()}`);
      }
    });
    page.on("pageerror", (error) => {
      consoleProblems.push(`pageerror: ${error.message}`);
    });

    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: /execute/i }).click();
    await expect(page.locator("#verdict-badge")).toContainText(/RED|STOP|GREEN|REVIEW/);
    await expect(page.locator("#telemetry-status-text")).toContainText(/COMPLETE/);
    await expect(page.getByRole("button", { name: /raw backend json/i })).toBeVisible();

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    expect(consoleProblems).toEqual([]);
  });
}
