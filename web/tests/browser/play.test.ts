import { test, expect } from "@playwright/test";
import type { Fight } from "../../src/fight";
declare global {
  interface Window {
    __omacontra: {
      fight: Fight;
      mode: string;
      metrics: { frames: number[]; sprites: number; slowFrames: number };
    };
  }
}
test("loads, moves, jumps, aims, pauses, recovers focus, and finishes", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/reaper.html");
  await expect(page.locator("#start")).toBeEnabled();
  await page.screenshot({
    path: `test-results/${testInfo.project.name}-title.png`,
  });
  await page.locator("#practice").check();
  await page.locator("#start").click();
  await expect(page.locator("#panel")).toBeHidden();
  await page.keyboard.down("d");
  await expect
    .poll(() => page.evaluate(() => window.__omacontra.fight.x))
    .toBeGreaterThan(230);
  await page.keyboard.up("d");
  await page.keyboard.down("Space");
  await expect
    .poll(() => page.evaluate(() => window.__omacontra.fight.y))
    .toBeLessThan(660);
  await page.keyboard.up("Space");
  await page.keyboard.press("Shift");
  await expect
    .poll(() => page.evaluate(() => window.__omacontra.fight.dashUsed))
    .toBe(true);
  const canvas = page.locator("canvas");
  const box = (await canvas.boundingBox())!;
  await page.mouse.move(box.x + box.width * 0.45, box.y + box.height * 0.32);
  await page.mouse.down();
  await expect
    .poll(() => page.evaluate(() => window.__omacontra.fight.shotsFired))
    .toBeGreaterThan(4);
  await page.mouse.up();
  await page.screenshot({
    path: `test-results/${testInfo.project.name}-combat.png`,
  });
  await page.keyboard.press("p");
  await expect(page.locator("#panel-title")).toHaveText("PAUSED");
  await page.evaluate(() =>
    window.dispatchEvent(
      new KeyboardEvent("keydown", { code: "KeyP", repeat: true }),
    ),
  );
  await expect(page.locator("#panel-title")).toHaveText("PAUSED");
  const clock = await page.evaluate(() => window.__omacontra.fight.clock);
  await page.waitForTimeout(150);
  expect(await page.evaluate(() => window.__omacontra.fight.clock)).toBe(clock);
  await page.locator("#start").click();
  await page.keyboard.down("d");
  await page.evaluate(() => window.dispatchEvent(new Event("blur")));
  await page.keyboard.up("d");
  await expect(page.locator("#panel-title")).toHaveText("PAUSED");
  await page.locator("#start").click();
  const before = await page.evaluate(() => window.__omacontra.fight.x);
  await page.keyboard.down("d");
  await expect
    .poll(() => page.evaluate(() => window.__omacontra.fight.x))
    .toBeGreaterThan(before + 10);
  await page.keyboard.up("d");
  await page.evaluate(() => {
    const f = window.__omacontra.fight;
    f.nodes = { eye: 0, raven: 0 };
    f.exposed = 11;
    f.hitTarget(...f.body, ...f.body, 180);
  });
  await expect(page.locator("#panel-title")).toHaveText("STAGE CLEAR", {
    timeout: 15_000,
  });
  await expect(page.locator("#result")).toContainText("PRACTICE");
  expect(
    await page.evaluate(() =>
      localStorage.getItem("omacontra.web.reaper.best"),
    ),
  ).toBeNull();
  await page.locator("#start").click();
  await expect(page.locator("#panel")).toBeHidden();
  expect(await canvas.getAttribute("width")).toBe("1280");
  expect(await canvas.getAttribute("height")).toBe("720");
  console.log(
    testInfo.project.name,
    await page.evaluate(() => {
      const m = window.__omacontra.metrics;
      const sorted = [...m.frames].sort((a, b) => a - b);
      return {
        p95: sorted[Math.floor(sorted.length * 0.95)],
        sprites: m.sprites,
        slowFrames: m.slowFrames,
      };
    }),
  );
  expect(errors).toEqual([]);
});
test("720p buffer stays fixed at high DPI", async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:5173/reaper.html");
  await expect(page.locator("#start")).toBeEnabled();
  expect(await page.locator("canvas").getAttribute("width")).toBe("1280");
  await context.close();
});
test("failed asset requests give a readable error", async ({ page }) => {
  await page.route("**/game/manifest.json", (route) =>
    route.fulfill({ status: 404, body: "missing" }),
  );
  await page.goto("/reaper.html");
  await expect(page.locator("#panel-title")).toHaveText("COULD NOT START");
  await expect(page.locator("#load-status")).toContainText(
    "Run npm run assets",
  );
});
test("standard clear stores a personal best and reload preserves it", async ({
  page,
}) => {
  await page.goto("/reaper.html");
  await expect(page.locator("#start")).toBeEnabled();
  await page.locator("#start").click();
  await expect(page.locator("#panel")).toBeHidden();
  await page.evaluate(() => {
    const f = window.__omacontra.fight;
    f.nodes = { eye: 0, raven: 0 };
    f.exposed = 11;
    f.hitTarget(...f.body, ...f.body, 180);
  });
  await expect(page.locator("#panel-title")).toHaveText("STAGE CLEAR", {
    timeout: 15_000,
  });
  await expect(page.locator("#result")).toContainText("BEST");
  const best = await page.evaluate(() =>
    localStorage.getItem("omacontra.web.reaper.best"),
  );
  expect(Number(best)).toBeGreaterThan(0);
  await page.reload();
  expect(
    await page.evaluate(() =>
      localStorage.getItem("omacontra.web.reaper.best"),
    ),
  ).toBe(best);
});
