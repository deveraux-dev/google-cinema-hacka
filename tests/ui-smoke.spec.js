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
  { name: "laptop", width: 1280, height: 900 },
  { name: "tablet", width: 768, height: 1024 },
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
    await expect(page.locator("#verdict-badge")).toHaveText("—");
    await expect(page.locator("#telemetry-status-text")).toContainText(/WAITING FOR REVISION/);
    await page.getByRole("button", { name: /analyze revision/i }).click();
    await expect(page.locator("#verdict-badge")).toContainText(/RED|STOP|GREEN|REVIEW/);
    await expect(page.locator("#telemetry-status-text")).toContainText(/COMPLETE/);
    await expect(page.locator("#chain-frontend")).toContainText(/Rendered .*JSON/);
    await expect(page.locator("#chain-safety")).toContainText(/RED|STOP|GREEN|REVIEW/);
    await expect(page.getByRole("button", { name: /raw backend json/i })).toBeVisible();

    await page.getByRole("button", { name: /raw backend json/i }).click();
    await expect(page.locator("#detail-modal")).toHaveClass(/active/);
    await page.keyboard.press("Escape");
    await expect(page.locator("#detail-modal")).not.toHaveClass(/active/);

    await page.getByRole("tab", { name: /custom revision/i }).click();
    await expect(page.locator("#custom-editor-panel")).toBeVisible();
    await page.getByRole("tab", { name: /scenario deck/i }).click();
    await expect(page.locator("#scenario-deck-panel")).toBeVisible();

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    expect(consoleProblems).toEqual([]);
  });
}

test("custom revision editor reaches the same verdict flow", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.getByRole("tab", { name: /custom revision/i }).click();
  await page.locator("#custom-orig-text").fill("INT. STAGE - DAY\nA quiet room.");
  await page.locator("#custom-rev-text").fill("INT. STAGE - DAY\nA practical flash pot explodes.");
  await page.getByRole("button", { name: /analyze revision/i }).click();
  await expect(page.locator("#verdict-badge")).toContainText(/RED|STOP|GREEN|REVIEW/);
  await expect(page.locator("#chain-frontend")).toContainText(/Rendered .*JSON/);
});

test("auto-review analyzes a newly selected scenario", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await expect(page.locator("#auto-review-toggle")).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: /confined space prop firearm shootout/i }).click();
  await expect(page.locator("#verdict-badge")).toContainText(/STOP/);
  await expect(page.locator("#term-logs")).toContainText(/Auto-review selected this revision/);
});

test("STOP verdict cannot be overridden by checking clearances", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /confined space prop firearm shootout/i }).click();
  await expect(page.locator("#verdict-badge")).toHaveText("STOP");

  const clearances = page.locator("#clears-container .clear-checkbox");
  for (const clearance of await clearances.all()) {
    await clearance.check();
  }

  await expect(page.locator("#gate-title")).toHaveText("MANDATORY STOP // SET FROZEN");
  await expect(page.locator("#gate-desc")).toContainText(/cannot authorize camera roll/i);
});

test("workspace navigation and stage depth remain usable", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await expect(page.locator(".quick-nav-link")).toHaveCount(4);
  await expect(page.locator(".stage-plate")).toHaveCount(3);
  await page.locator('[data-section-link="technical-proof"]').click();
  await expect(page.locator("#technical-proof")).toBeInViewport();
  await page.evaluate(() => window.scrollTo(0, 0));
  const plateY = await page.locator(".stage-plate-one").evaluate((node) => getComputedStyle(node).getPropertyValue("--plate-y"));
  expect(plateY).toBeTruthy();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});
