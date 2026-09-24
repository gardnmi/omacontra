import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Fight, FLOOR, STEP, segmentBox, type Controls } from "../src/fight";
import { Input } from "../src/input";
const traces = JSON.parse(
  readFileSync(new URL("./desktop-traces.json", import.meta.url), "utf8"),
);
function compare(actual: unknown, expected: unknown, path: string) {
  if (typeof expected === "number")
    assert.ok(
      typeof actual === "number" && Math.abs(actual - expected) < 1e-6,
      `${path}: ${actual} != ${expected}`,
    );
  else if (expected && typeof expected === "object")
    for (const [key, value] of Object.entries(expected))
      compare(
        (actual as Record<string, unknown>)[key],
        value,
        `${path}.${key}`,
      );
  else assert.equal(actual, expected, path);
}
for (const trace of traces)
  test(`matches desktop trace: ${trace.name}`, () => {
    const f = new Fight();
    f.invuln = 999;
    for (let frame = 0; frame < trace.actions.length; frame++) {
      const action = trace.actions[frame];
      f.step(STEP, { ...action, aimUp: action.aim_up } as Controls);
      f.events.length = 0;
      const expected = trace.snapshots.find(
        (s: { frame: number }) => s.frame === frame,
      );
      if (expected) {
        compare(f, expected.values, `${trace.name}:${frame}`);
        const shots = f.shots.map((b) => [b.x, b.y, b.vx, b.vy, b.kind]);
        assert.equal(shots.length, expected.shots.length, `shots at ${frame}`);
        compare(shots, expected.shots, `shots:${frame}`);
      }
    }
  });
test("fast bullets cannot tunnel through a body", () => {
  assert.ok(segmentBox(0, 20, 1000, 20, [40, 10, 60, 30]));
  assert.ok(!segmentBox(0, 40, 1000, 40, [40, 10, 60, 30]));
});
test("jump then air dash clears the broad sweep without dash invulnerability", () => {
  const f = new Fight();
  f.invuln = 0;
  f.step(STEP, { jump: true });
  for (let i = 0; i < 12; i++) f.step(STEP);
  f.step(STEP, { slide: true, move: 1 });
  assert.ok(f.dashUsed);
  assert.ok(f.y < FLOOR - 68);
  f.spawn(f.x, FLOOR - 34, -200, 0, true, "scythe_dash", 7);
  f.step(STEP, { move: 1 });
  assert.equal(f.damageTaken, 0);
  const g = new Fight();
  g.invuln = 0;
  g.spawn(g.x, FLOOR - 34, -200, 0, true, "scythe_dash", 7);
  g.step(STEP, { slide: true });
  assert.equal(g.damageTaken, 1);
});
test("no third jump or second air dash before landing", () => {
  const f = new Fight();
  f.step(STEP, { jump: true });
  f.step(STEP);
  f.step(STEP, { jump: true });
  f.step(STEP);
  f.step(STEP, { jump: true });
  assert.equal(f.jumpsUsed, 2);
  f.step(STEP, { slide: true });
  for (let i = 0; i < 15; i++) f.step(STEP);
  f.step(STEP, { slide: true });
  assert.equal(f.dashTime, 0);
});
test("turrets shield the core, reform after exposure, and final hit clears danger", () => {
  const f = new Fight();
  let [x, y] = f.body;
  f.hitTarget(x, y, x, y);
  assert.equal(f.bossHp, 180);
  for (const role of ["eye", "raven"] as const) {
    [x, y] = f.nodeCenter(role);
    f.hitTarget(x, y, x, y, 12);
  }
  assert.equal(f.shielded, false);
  [x, y] = f.body;
  f.hitTarget(x, y, x, y, 1);
  assert.equal(f.bossHp, 179);
  f.exposed = 0.001;
  f.step(STEP);
  assert.equal(f.shielded, true);
  f.nodes = { eye: 0, raven: 0 };
  f.exposed = 11;
  f.spawn(180, FLOOR - 20, 0, 0, true);
  [x, y] = f.body;
  f.hitTarget(x, y, x, y, 180);
  assert.equal(f.state, "dying");
  assert.ok(f.shots.every((b) => b.life <= 0));
  for (let i = 0; i < 260; i++) f.step(STEP);
  assert.equal(f.state, "won");
});
test("unlimited runs count damage, keep lives, and recover", () => {
  const f = new Fight();
  f.unlimited = true;
  f.invuln = 0;
  f.hurt();
  assert.equal(f.damageTaken, 1);
  assert.equal(f.hp, 5);
  f.hurt();
  assert.equal(f.damageTaken, 1);
  for (let i = 0; i < 40; i++) f.step(STEP);
  assert.equal(f.hitAge, null);
  assert.ok(f.invuln > 2);
  assert.equal(f.y, FLOOR);
});
test("input consume suppresses repeats, focus reset permits a fresh press", () => {
  const i = new Input();
  assert.ok(i.down("Space"));
  i.consume();
  assert.equal(i.down("Space"), false);
  assert.equal(i.controls().jump, false);
  i.clear();
  assert.ok(i.down("Space"));
  assert.equal(i.controls().jump, true);
});
test("sustained fire remains bounded without growing particle or shot pools", () => {
  const f = new Fight();
  f.unlimited = true;
  for (let i = 0; i < 60 * 180; i++) {
    f.step(STEP, {
      shoot: true,
      move: Math.sin(i * 0.01) > 0 ? 1 : -1,
      jump: i % 60 === 0,
    });
    f.events.length = 0;
    assert.ok(f.shots.length <= 350);
    assert.ok(f.particles.length <= 300);
  }
});
