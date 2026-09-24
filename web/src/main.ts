import "./style.css";
import { Fight, STEP, CUES } from "./fight";
import { Scene, type Manifest } from "./renderer";
import { GameAudio } from "./audio";
import { Input } from "./input";
const el = <T extends HTMLElement = HTMLElement>(id: string) =>
  document.getElementById(id) as T;
const game = el("game"),
  panel = el("panel"),
  start = el<HTMLButtonElement>("start"),
  restart = el<HTMLButtonElement>("restart");
const input = new Input(),
  audio = new GameAudio(),
  scene = new Scene();
let fight = new Fight(),
  mode: "title" | "playing" | "paused" | "result" = "title",
  ready = false,
  busy = false;
let manifest: Manifest,
  last = 0,
  accumulator = 0,
  metricsClock = 0,
  renders = 0,
  slowFrames = 0;
let stats = false,
  finished = false,
  savedBest: number | null = null;
const frameTimes: number[] = [];
let renderCost = 0;
function text(id: string, value: string) {
  const node = el(id);
  if (node.textContent !== value) node.textContent = value;
}
function saveResult() {
  if (fight.unlimited) return;
  try {
    const value = Number(localStorage.getItem("omacontra.web.reaper.best"));
    savedBest = value > 0 ? Math.min(value, fight.clock) : fight.clock;
    localStorage.setItem("omacontra.web.reaper.best", String(savedBest));
  } catch {
    savedBest = null;
  }
}
function showPanel(title: string, copy: string, button: string) {
  text("panel-title", title);
  text("panel-copy", copy);
  start.textContent = button;
  panel.hidden = false;
  el("instructions").hidden = mode === "result";
  el("practice-row").hidden = true;
  el("load-status").hidden = true;
  restart.hidden = mode !== "paused";
  start.focus({ preventScroll: true });
}
function pause() {
  if (mode !== "playing") return;
  mode = "paused";
  input.consume();
  accumulator = 0;
  audio.pause();
  showPanel("PAUSED", "Take a breath. The Reaper can wait.", "RESUME");
}
function resume() {
  mode = "playing";
  input.consume();
  panel.hidden = true;
  accumulator = 0;
  last = performance.now();
  void audio.resume();
}
function newFight() {
  audio.clear();
  fight = new Fight();
  fight.unlimited = el<HTMLInputElement>("practice").checked;
  finished = false;
  savedBest = null;
  text("result", "");
  input.clear();
  resume();
  el("hud").hidden = false;
}
async function activate() {
  if (!ready || busy) return;
  if (mode === "paused") {
    resume();
    return;
  }
  busy = true;
  start.disabled = true;
  text("load-status", "PREPARING SOUND…");
  el("load-status").hidden = false;
  try {
    await audio.init(manifest);
  } catch (error) {
    console.warn("Audio unavailable; playing silently", error);
    audio.setMuted(true);
    text("mute", "SOUND OFF");
  }
  busy = false;
  start.disabled = false;
  newFight();
  if (document.hidden || !document.hasFocus()) pause();
}
start.addEventListener("click", () => void activate());
restart.addEventListener("click", newFight);
el("mute").addEventListener("click", () => {
  audio.setMuted(!audio.muted);
  text("mute", audio.muted ? "SOUND OFF" : "SOUND ON");
  el("mute").setAttribute("aria-pressed", String(audio.muted));
});
el("stats").addEventListener("click", () => {
  stats = !stats;
  el("performance").hidden = !stats;
  el("stats").setAttribute("aria-pressed", String(stats));
});
el("fullscreen").addEventListener("click", async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await game.requestFullscreen();
  } catch {
    text("load-status", "Fullscreen is unavailable in this browser.");
  }
});
const gameCodes = new Set([
  "KeyA",
  "KeyD",
  "KeyS",
  "KeyW",
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "ArrowDown",
  "Space",
  "KeyK",
  "KeyJ",
  "KeyZ",
  "ShiftLeft",
  "ShiftRight",
  "KeyP",
  "Escape",
  "KeyR",
  "Enter",
  "F3",
]);
window.addEventListener("keydown", (e) => {
  if (!gameCodes.has(e.code) || e.target instanceof HTMLInputElement) return;
  if (
    e.target instanceof HTMLButtonElement &&
    mode !== "playing" &&
    ["Enter", "Space"].includes(e.code)
  )
    return;
  e.preventDefault();
  if (e.repeat || !input.down(e.code)) return;
  if (e.code === "F3") {
    el("stats").click();
    return;
  }
  if (e.code === "Escape" || e.code === "KeyP") {
    if (mode === "playing") pause();
    else if (mode === "paused") resume();
    return;
  }
  if (e.code === "Enter" && mode !== "playing") void activate();
  if (e.code === "KeyR" && mode !== "title") {
    if (mode === "playing") pause();
    else newFight();
  }
});
window.addEventListener("keyup", (e) => input.up(e.code));
function pointer(e: PointerEvent) {
  const rect = scene.app.canvas.getBoundingClientRect();
  input.aim = [
    ((e.clientX - rect.left) * 1280) / rect.width,
    ((e.clientY - rect.top) * 720) / rect.height,
  ];
}
game.addEventListener("pointermove", (e) => {
  if (ready) pointer(e);
});
game.addEventListener("pointerdown", (e) => {
  if (mode !== "playing" || e.button !== 0) return;
  e.preventDefault();
  pointer(e);
  input.mouse = true;
  game.setPointerCapture(e.pointerId);
  (document.activeElement as HTMLElement)?.blur();
});
window.addEventListener("pointerup", (e) => {
  if (e.button === 0) input.mouse = false;
});
game.addEventListener("pointercancel", () => {
  input.mouse = false;
});
game.addEventListener("lostpointercapture", () => {
  input.mouse = false;
});
game.addEventListener("contextmenu", (e) => e.preventDefault());
window.addEventListener("blur", () => {
  input.clear();
  pause();
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    input.clear();
    pause();
    audio.pause();
  }
  last = performance.now();
  accumulator = 0;
});
function hud() {
  text(
    "phase",
    `PHASE ${fight.phase} / ${fight.state === "won" ? "DEFEATED" : fight.shielded ? "SHIELDED" : "CORE EXPOSED"}`,
  );
  el("boss-health").style.width = `${(100 * fight.bossHp) / fight.bossMax}%`;
  text(
    "lives",
    fight.unlimited
      ? `∞   HITS ${fight.damageTaken}`
      : `${"▣ ".repeat(Math.max(0, fight.hp))}  ${fight.hp}`,
  );
  text(
    "ability",
    `AIR DASH ${fight.dashUsed ? "USED" : "READY"}${fight.slideCooldown > 0 ? " · SLIDE RECHARGING" : ""}`,
  );
  text("notice", fight.noticeTime > 0 ? fight.notice : "");
  text(
    "warning",
    fight.warning === "scythe"
      ? `SCYTHE / ${fight.pattern.map((p) => CUES[p]).join(" → ")}`
      : fight.warning === "aimed"
        ? "EYE LOCK / KEEP MOVING"
        : fight.warning === "raven"
          ? "RAVENS INBOUND"
          : "",
  );
}
function loop(now: number) {
  requestAnimationFrame(loop);
  const elapsed = last ? (now - last) / 1000 : 0;
  last = now;
  if (!ready || document.hidden) return;
  if (mode === "playing") {
    frameTimes.push(elapsed * 1000);
    if (frameTimes.length > 180) frameTimes.shift();
    accumulator += Math.min(0.1, elapsed);
    let steps = 0;
    while (accumulator >= STEP && steps < 5) {
      fight.step(STEP, input.controls());
      audio.play(fight.events);
      accumulator -= STEP;
      steps++;
    }
    if (accumulator >= STEP) {
      accumulator %= STEP;
      slowFrames++;
    }
    const began = performance.now();
    scene.draw(fight, accumulator / STEP);
    renderCost = performance.now() - began;
    renders++;
    hud();
    if (!finished && (fight.state === "dead" || fight.state === "won")) {
      finished = true;
      mode = "result";
      input.consume();
      if (fight.state === "won") saveResult();
      showPanel(
        fight.state === "won" ? "STAGE CLEAR" : "DHH DOWN",
        fight.state === "won"
          ? "MERGE IT. The Reaper encounter is complete."
          : "The wallpaper wins this round. Get back in the fight.",
        "PLAY AGAIN",
      );
      text(
        "result",
        `${fight.unlimited ? "PRACTICE · " : ""}TIME ${fight.clock.toFixed(1)}s · HITS ${fight.damageTaken}${savedBest ? ` · BEST ${savedBest.toFixed(1)}s` : ""}`,
      );
    }
  }
  if (now - metricsClock >= 500) {
    const sorted = [...frameTimes].sort((a, b) => a - b),
      p95 = sorted[Math.floor(sorted.length * 0.95)] ?? 0;
    text(
      "performance",
      `WEBGL · 1280 × 720\n${((renders * 1000) / Math.max(1, now - metricsClock)).toFixed(0)} FPS · p95 ${p95.toFixed(1)} ms\nRender CPU ${renderCost.toFixed(1)} ms · ${scene.spriteCount} sprites\nCatch-up drops ${slowFrames} · FX ${fight.effectsScale === 1 ? "FULL" : "REDUCED"}`,
    );
    if (frameTimes.length >= 120 && p95 > 24) fight.effectsScale = 0.5;
    metricsClock = now;
    renders = 0;
  }
}
async function boot() {
  try {
    const response = await fetch("game/manifest.json");
    if (!response.ok)
      throw new Error("Missing web assets. Run npm run assets first.");
    manifest = await response.json();
    await scene.init(game, manifest, (value) => text("load-status", value));
    scene.draw(fight, 1);
    ready = true;
    start.disabled = false;
    start.textContent = "ENTER THE FIGHT";
    text("load-status", "READY / 720p · KEYBOARD & MOUSE");
    scene.app.canvas.addEventListener("webglcontextlost", (e) => {
      e.preventDefault();
      pause();
      text("panel-copy", "Graphics context lost. Reload this page to recover.");
      start.disabled = true;
    });
    if (import.meta.env.DEV)
      Object.defineProperty(window, "__omacontra", {
        value: {
          get fight() {
            return fight;
          },
          get mode() {
            return mode;
          },
          input,
          get metrics() {
            return {
              frames: frameTimes.slice(),
              sprites: scene.spriteCount,
              slowFrames,
            };
          },
        },
      });
  } catch (error) {
    text("panel-title", "COULD NOT START");
    text("load-status", error instanceof Error ? error.message : String(error));
    text(
      "panel-copy",
      "This playtest needs a WebGL-capable browser. If assets are missing, run npm run assets, then reload.",
    );
    console.error(error);
  }
}
requestAnimationFrame(loop);
void boot();
