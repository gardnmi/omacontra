import { test, expect, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
declare global {
  interface Window {
    __campaign: any;
  }
}
const state = (page: Page) => page.evaluate(() => window.__campaign.status);
const debug = (page: Page, action: string, values: any = {}) =>
  page.evaluate(([a, v]) => window.__campaign.debug(a, v), [action, values]);
const script = (page: Page, code: string) => debug(page, "script", { code });
async function boot(page: Page) {
  await page.goto("/");
  await expect(page.locator("#play")).toBeVisible({ timeout: 30000 });
  await page.locator("#play").click();
  await expect(page.locator("#gate")).toBeHidden();
}
test.beforeEach(async ({ page }) => {
  page.on("pageerror", (e) => {
    throw e;
  });
});
test("original opening, secret code, mode selection, journey and controls", async ({
  page,
}) => {
  await boot(page);
  for (const key of [
    "ArrowUp",
    "ArrowUp",
    "ArrowDown",
    "ArrowDown",
    "ArrowLeft",
    "ArrowRight",
    "ArrowLeft",
    "ArrowRight",
  ])
    await page.keyboard.press(key);
  await expect.poll(async () => (await state(page)).unlimited).toBe(true);
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) => m.active && m.track.includes("unlock"),
        ),
      ),
    )
    .toBe(true);
  for (let i = 0; i < 6; i++) await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).intro).toBe("cover");
  await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).menu).toBe("mode");
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) =>
            m.active && !m.paused && m.track.includes("opening-theme"),
        ),
      ),
    )
    .toBe(true);
  await page.keyboard.press("Enter");
  await expect
    .poll(async () => (await state(page)).journey, { timeout: 6000 })
    .toBe(true);
  for (let i = 0; i < 5; i++) await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).intro).toBe(null);
  const x = (await state(page)).x;
  await page.keyboard.down("d");
  await expect.poll(async () => (await state(page)).x).toBeGreaterThan(x + 25);
  await page.keyboard.up("d");
  await page.keyboard.press("Space");
  await expect.poll(async () => (await state(page)).y).toBeLessThan(670);
  await page.keyboard.press("Shift");
  await page.keyboard.down("j");
  await expect.poll(async () => (await state(page)).shots).toBeGreaterThan(0);
  await page.keyboard.up("j");
  await page.keyboard.press("Escape");
  await expect.poll(async () => (await state(page)).menu).toBe("pause");
  const clock = (await state(page)).clock;
  await page.waitForTimeout(150);
  expect((await state(page)).clock).toBe(clock);
  await page.keyboard.press("Escape");
  await expect.poll(async () => (await state(page)).paused).toBe(false);
  await page.evaluate(() => window.dispatchEvent(new Event("blur")));
  await expect.poll(async () => (await state(page)).menu).toBe("pause");
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await page.keyboard.press("Escape");
  await expect.poll(async () => (await state(page)).paused).toBe(false);
});
test("all five encounters, uninterrupted progression, final music and results", async ({
  page,
}) => {
  await boot(page);
  await debug(page, "stage", { level: 1, skip: true });
  await script(page, "app.frontend.new_run()\napp.f.hp=3\napp.f.invuln=999");
  for (let level = 1; level < 5; level++) {
    if (level === 3) {
      await debug(page, "guardians");
      expect((await state(page)).stage).toBe(1);
      await script(
        page,
        "app.f.wave_reveal=0\napp.f.guardians[0].hp=0\napp.f.step(.02)",
      );
    }
    await script(page, 'app.f.state="won"');
    await expect.poll(async () => (await state(page)).cleared).toContain(level);
    if (level === 2) await script(page, "app.chase_cinema.age=6");
    if (level === 3) await script(page, "app.journey_cinema.age=6");
    const hp = (await state(page)).hp;
    await page.keyboard.press("Enter");
    await expect.poll(async () => (await state(page)).level).toBe(level + 1);
    expect((await state(page)).hp).toBe(hp + 1);
    if (level < 4) {
      await page.keyboard.press("Enter");
      await expect.poll(async () => (await state(page)).cinema).toBe(null);
      await script(page, "app.f.invuln=999");
    }
  }
  expect((await state(page)).state).toBe("departure");
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) => m.active && !m.paused && m.track.includes("oligarchy"),
        ),
      ),
    )
    .toBe(true);
  await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).state).toBe("encounter");
  await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).state).toBe("play");
  await script(page, "app.f.nodes=[0,0]\napp.f.boss_hp=300\napp.f.invuln=999");
  for (const t of [2, 8, 20]) {
    await script(page, `app.f.screensaver_age=${t}`);
    expect((await state(page)).phase).toBe(3);
  }
  await script(page, "app.f.boss_hp=0");
  await expect.poll(async () => (await state(page)).state).toBe("ending");
  await script(page, "app.f.age=23");
  await expect
    .poll(async () => (await state(page)).menu, { timeout: 7000 })
    .toBe("results");
  expect((await state(page)).cleared).toEqual([1, 2, 3, 4, 5]);
  expect((await state(page)).category).toBe("arcade");
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) => m.active && !m.paused && m.track.includes("oligarchy"),
        ),
      ),
    )
    .toBe(true);
  expect(
    await page.evaluate(
      () =>
        JSON.parse(localStorage.getItem("omacontra.campaign.profile.v1")!).best
          .arcade,
    ),
  ).toBeGreaterThan(0);
});
test("continue, hardcore, unlimited damage tracking, persisted options and soundtrack", async ({
  page,
}) => {
  await boot(page);
  await debug(page, "stage", { level: 1, skip: true });
  await script(page, 'app.f.state="dead"\napp.f.hp=0\napp.death_wait=2');
  await expect.poll(async () => (await state(page)).continue).toBe("countdown");
  await page.keyboard.press("Enter");
  await expect.poll(async () => (await state(page)).continues).toBe(1);
  expect((await state(page)).hp).toBeGreaterThan(0);
  await script(
    page,
    "app.unlimited_lives=True\napp.f.unlimited_lives=True\napp.f.invuln=0\napp.f.damage_taken=4\napp.frontend.record.observe(1,.1,1,0,True,True)",
  );
  expect((await state(page)).losses).toBe(1);
  await script(
    page,
    'app.frontend.record.hardcore=True\napp.f.state="dead"\napp.f.hp=0\napp.death_wait=2',
  );
  await expect.poll(async () => (await state(page)).continue).toBe("expired");
  await debug(page, "stage", { level: 1, skip: true });
  expect((await state(page)).settings).toEqual({ music: 60, effects: 100 });
  await debug(page, "menu", { page: "options" });
  await page.keyboard.press("ArrowLeft");
  await expect.poll(async () => (await state(page)).settings.music).toBe(55);
  await debug(page, "menu", { page: "music" });
  await page.keyboard.press("Enter");
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) => m.active && !m.paused && m.track.includes("wine-cellar"),
        ),
      ),
    )
    .toBe(true);
  await page.keyboard.press("ArrowRight");
  await expect
    .poll(() =>
      page.evaluate(() =>
        window.__campaign.music.some(
          (m: any) => m.active && !m.paused && m.track === "audio/contra.opus",
        ),
      ),
    )
    .toBe(true);
  await page.reload();
  await expect(page.locator("#play")).toBeVisible({ timeout: 30000 });
  expect((await state(page)).settings.music).toBe(55);
});
test("native renderer review states, all cinematic panels and menu pages", async ({
  page,
}, info) => {
  test.setTimeout(120000);
  await page.setViewportSize({ width: 1280, height: 766 });
  await boot(page);
  await page.evaluate(() => window.__campaign.stop());
  const source = readFileSync("../tools/asset_review.py", "utf8");
  await script(
    page,
    `review_ns={'__name__':'review','__file__':'/game/tools/asset_review.py'}\nexec(${JSON.stringify(source)},review_ns)\nreview=iter(review_ns['scenes']())`,
  );
  for (let i = 0; i < 12; i++) {
    await script(
      page,
      "review_name,review_draw,review_f=next(review)\napp.draw=lambda area,c:review_draw(c,review_f)",
    );
    await page
      .locator("#game")
      .screenshot({
        path: `test-results/${info.project.name}-native-scene-${i}.png`,
      });
  }
  await script(page, "del app.draw");
  // Boundaries that are absent from the static art sheet: transformations,
  // both rage portraits, and Tobi's complete rescue timeline.
  await debug(page, "stage", { level: 2, skip: true });
  await script(page, "app.f.detach_trailer()");
  for (const age of [0.1, 0.8, 2.6, 3.3])
    await script(page, `app.f.transform_age=${age}`);
  await script(
    page,
    "from omacontra.stages.highway import chase_robot\nchase_robot.transform_step(app.f,.2)",
  );
  for (const age of [1, 3.3, 5.5])
    await script(page, `app.f.robot_age=${age}\napp.f.jump_height=260`);
  await script(page, "app.f.begin_finisher()");
  await script(page, "app.f.begin_destruction()\napp.f.death_age=1.8");
  for (const survivor of [0, 1]) {
    await debug(page, "stage", { level: 3, skip: true });
    await debug(page, "guardians");
    for (const age of [0.1, 1.2, 2.5, 4])
      await script(
        page,
        `app.f.wave_reveal=0\napp.f.guardians[${1 - survivor}].hp=0\napp.f.guardians[${survivor}].enraged=True\napp.f.guardians[${survivor}].rage_age=${age}`,
      );
  }
  await debug(page, "stage", { level: 4, skip: true });
  await script(page, "app.f.begin_rescue()");
  for (const age of [
    0, 0.01, 1.25, 3.2, 4.25, 5.34, 5.35, 5.45, 6, 7.5, 9.1, 13.5,
  ])
    await script(page, `app.f.rescue_age=${age}`);
  for (let index = 0; index < 7; index++)
    await debug(page, "intro", { index, age: 3 });
  for (let index = 0; index < 5; index++)
    await script(
      page,
      `from omacontra.ui.story import Intro\napp.intro=Intro(journey=True)\napp.intro.index=${index}\napp.intro.age=3`,
    );
  for (const level of [2, 3, 4]) {
    await debug(page, "stage", { level });
    await script(
      page,
      `getattr(app,${JSON.stringify({ 2: "chase_cinema", 3: "journey_cinema", 4: "foundry_intro" }[level as 2 | 3 | 4])}).age=4`,
    );
  }
  await debug(page, "stage", { level: 5 });
  for (const age of [4, 8, 12, 16, 21]) await script(page, `app.f.age=${age}`);
  await script(page, "app.f.begin_encounter()\napp.f.age=8");
  for (const age of [1, 8, 17, 21])
    await script(page, `app.f.state="ending"\napp.f.age=${age}`);
  for (const menu of [
    "pause",
    "controls",
    "options",
    "music",
    "credits",
    "results",
    "bosses",
    "mode",
  ])
    await debug(page, "menu", { page: menu });
  for (const credits of [0, 1, 2])
    await script(
      page,
      `app.frontend.page="credits"\napp.frontend.credits_page=${credits}`,
    );
  await script(page, "app.frontend.page=None");
  await debug(page, "continue");
  await script(
    page,
    "app.continue_screen.accept()\napp.continue_screen.age=.65",
  );
});
test("high DPI stays 720p, unavailable storage is safe, and loading errors are visible", async ({
  browser,
}) => {
  const context = await browser.newContext({ deviceScaleFactor: 2 });
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new Error("disabled");
      },
    });
  });
  await boot(page);
  expect(
    await page
      .locator("#game")
      .evaluate((c: HTMLCanvasElement) => [c.width, c.height]),
  ).toEqual([1280, 720]);
  await debug(page, "menu", { page: "options" });
  await page.keyboard.press("ArrowLeft");
  await expect.poll(async () => (await state(page)).settings.music).toBe(55);
  await context.close();
  const broken = await browser.newPage();
  await broken.route("**/campaign/game.zip", (route) =>
    route.fulfill({ status: 404, body: "missing" }),
  );
  await broken.goto("/");
  await expect(broken.locator("#loading")).toContainText(
    "Campaign archive is missing",
    { timeout: 30000 },
  );
  await broken.close();
});
