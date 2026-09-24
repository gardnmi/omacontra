import "./style.css";
import { CampaignAudio } from "./audio";
const canvas = document.querySelector<HTMLCanvasElement>("#game")!,
  ctx = canvas.getContext("bitmaprenderer")!;
const gate = document.querySelector<HTMLElement>("#gate")!,
  loading = document.querySelector<HTMLElement>("#loading")!,
  play = document.querySelector<HTMLButtonElement>("#play")!;
const root = new URL(`${import.meta.env.BASE_URL}campaign/`, location.href)
  .href;
const audio = new CampaignAudio(root),
  worker = new Worker(new URL("./worker.ts", import.meta.url), {
    type: "module",
  });
const profileKey = "omacontra.campaign.profile.v1";
let profile: string | null = null;
try {
  profile = localStorage.getItem(profileKey);
} catch {}
let active = false,
  inflight = true,
  last = 0,
  request = 0,
  status: any,
  perf: any,
  failed = false,
  level = 0;
let events: any[] = [];
const samples: number[] = [];
const keys = new Map<string, number>();
let nextCode = 1;
const pending = new Map<
  number,
  { resolve: (value: any) => void; reject: (reason: any) => void }
>();
function send(message: any) {
  inflight = true;
  const id = ++request;
  worker.postMessage({ ...message, request: id });
  return id;
}
function fatal(message: string) {
  failed = true;
  gate.dataset.state = "error";
  gate.setAttribute("aria-busy", "false");
  for (const p of pending.values()) p.reject(new Error(message));
  pending.clear();
  gate.hidden = false;
  play.hidden = false;
  play.textContent = "RELOAD";
  loading.textContent = message.includes("Campaign archive is missing")
    ? "Campaign archive is missing. Run npm run assets, then reload."
    : "The game could not load or continue. Please reload and check your connection. Browser details are in the console.";
  audio.visibility(true);
  console.error(message);
}
worker.onerror = (e) => fatal(e.message);
worker.onmessage = (e) => {
  const data = e.data;
  if (data.type === "error") {
    fatal(data.message);
    console.error(data.detail);
    return;
  }
  if (data.type === "loading") {
    loading.textContent = data.message;
    return;
  }
  if (data.type !== "frame") return;
  inflight = false;
  ctx.transferFromImageBitmap(data.bitmap);
  status = data.status;
  perf = data.performance;
  samples.push(perf.simulation + perf.render);
  if (samples.length > 300) samples.shift();
  audio.process(data.audio, data.music);
  if (level !== status.level) {
    level = status.level;
    audio.preload(level);
  }
  if (data.profile)
    try {
      localStorage.setItem(profileKey, data.profile);
    } catch {
      events.push({ type: "storage-error" });
    }
  pending.get(data.request)?.resolve(status);
  pending.delete(data.request);
  if (!active) {
    gate.dataset.state = "ready";
    gate.setAttribute("aria-busy", "false");
    loading.textContent = "DHH is ready. Let’s go.";
    play.hidden = false;
  }
  if (status.closed) {
    active = false;
    gate.hidden = false;
    loading.textContent = "Thanks for playing.";
    play.textContent = "PLAY AGAIN";
  }
  if (perf.simulation + perf.render > 150) last = performance.now();
};
worker.postMessage({ type: "boot", root, profile, request: 0 });
play.addEventListener("click", async () => {
  if (failed) {
    location.reload();
    return;
  }
  await audio.unlock();
  active = true;
  gate.hidden = true;
  canvas.focus();
  last = performance.now();
  events.push({ type: "focus" });
  if (status?.closed) events.push({ type: "restart-session" });
});
function animate(now: number) {
  requestAnimationFrame(animate);
  if (!active || failed || inflight || pending.size) return;
  const dt = Math.min(0.04, (now - last) / 1000);
  last = now;
  send({ type: "tick", dt, events: events.splice(0) });
}
requestAnimationFrame(animate);
function name(e: KeyboardEvent) {
  return (
    (
      {
        ArrowUp: "Up",
        ArrowDown: "Down",
        ArrowLeft: "Left",
        ArrowRight: "Right",
        Space: "space",
        Enter: "Return",
        Escape: "Escape",
        ShiftLeft: "Shift_L",
        ShiftRight: "Shift_R",
      } as Record<string, string>
    )[e.code] ?? e.key
  );
}
for (const kind of ["keydown", "keyup"] as const)
  window.addEventListener(kind, (e) => {
    if (!active) return;
    if (
      [
        "Space",
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "Tab",
      ].includes(e.code)
    )
      e.preventDefault();
    if (e.repeat) return;
    if (!keys.has(e.code)) keys.set(e.code, nextCode++);
    events.push({
      type: kind === "keydown" ? "down" : "up",
      code: keys.get(e.code),
      key: name(e),
    });
  });
function point(e: MouseEvent) {
  const r = canvas.getBoundingClientRect();
  return {
    x: ((e.clientX - r.left) * 1280) / r.width,
    y: ((e.clientY - r.top) * 720) / r.height,
  };
}
canvas.addEventListener("mousemove", (e) => {
  if (active) {
    if (events.at(-1)?.type === "motion") events.pop();
    events.push({ type: "motion", ...point(e) });
  }
});
canvas.addEventListener("mousedown", (e) => {
  if (active) {
    canvas.focus();
    events.push({ type: "press", ...point(e), button: e.button + 1 });
  }
});
window.addEventListener("mouseup", (e) => {
  if (active)
    events.push({ type: "release", ...point(e), button: e.button + 1 });
});
canvas.addEventListener("contextmenu", (e) => e.preventDefault());
window.addEventListener("blur", () => {
  if (active) events.push({ type: "blur" });
  audio.visibility(true);
});
window.addEventListener("focus", () => {
  if (active) events.push({ type: "focus" });
  audio.visibility(false);
  last = performance.now();
});
document.addEventListener("visibilitychange", () => {
  audio.visibility(document.hidden);
  if (active) events.push({ type: document.hidden ? "blur" : "focus" });
  last = performance.now();
});
document.querySelector("#fullscreen")!.addEventListener("click", async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.body.requestFullscreen();
  } catch {}
  canvas.focus();
});
if (import.meta.env.DEV)
  (window as any).__campaign = {
    get status() {
      return status;
    },
    get performance() {
      return { ...perf, samples: [...samples] };
    },
    get music() {
      return audio.snapshot();
    },
    async debug(action: string, values: any = {}) {
      while (inflight) await new Promise((r) => setTimeout(r, 10));
      if (failed) throw new Error(loading.textContent!);
      return new Promise((resolve, reject) => {
        const id = send({ type: "debug", action, values });
        pending.set(id, { resolve, reject });
      });
    },
    stop() {
      active = false;
    },
    start() {
      active = true;
      last = performance.now();
    },
    input(event: any) {
      events.push(event);
    },
  };
