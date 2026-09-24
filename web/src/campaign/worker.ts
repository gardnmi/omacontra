import { CanvasBackend } from "./canvas";
const scope = globalThis as any;
let py: any, host: any, tick: any, debug: any, backend: CanvasBackend;
let chain = Promise.resolve();
async function frame(raw: string, request: number, start: number) {
  const data = JSON.parse(raw),
    simulation = performance.now() - start;
  const draw = JSON.parse(data.draw);
  delete data.draw;
  const renderStart = performance.now(),
    bitmap = await backend.execute(draw, data.surface);
  scope.postMessage(
    {
      type: "frame",
      request,
      ...data,
      bitmap,
      performance: {
        simulation,
        render: performance.now() - renderStart,
        bytes: backend.memoryBytes,
        commands: draw.commands.length,
      },
    },
    [bitmap],
  );
}
scope.onmessage = (event: MessageEvent) => {
  const data = event.data;
  chain = chain
    .then(async () => {
      if (data.type === "boot") {
        const root = data.root;
        backend = new CanvasBackend(root);
        scope.cairo_pixels = (...args: any[]) =>
          backend.pixels(args[0], args[1], args[2], args[3], args[4]);
        scope.cairo_measure = (text: string, size: number, bold: boolean) => {
          backend.measure.font = `${bold ? "bold " : ""}${size}px monospace`;
          return backend.measure.measureText(text).width;
        };
        scope.postMessage({
          type: "loading",
          message: "Loading the game runtime…",
        });
        const { loadPyodide } = await import(
          /* @vite-ignore */ `${root}python/pyodide.mjs`
        );
        py = await loadPyodide({ indexURL: `${root}python/` });
        scope.postMessage({
          type: "loading",
          message: "Loading the campaign…",
        });
        const response = await fetch(`${root}game.zip`);
        if (!response.ok)
          throw new Error("Campaign archive is missing. Run npm run assets.");
        py.unpackArchive(await response.arrayBuffer(), "zip", {
          extractDir: "/game",
        });
        await py.runPythonAsync(
          "import sys\nsys.path[:0]=['/game/runtime','/game/src']\nimport browser_host",
        );
        host = py.pyimport("browser_host");
        tick = host.tick;
        if (import.meta.env.DEV) debug = host.debug;
        const start = performance.now();
        await frame(host.boot(data.profile ?? null, 0), data.request, start);
      } else if (data.type === "tick") {
        const events = py.toPy(data.events);
        const start = performance.now();
        try {
          await frame(tick(data.dt, events), data.request, start);
        } finally {
          events.destroy();
        }
      } else if (data.type === "debug" && import.meta.env.DEV) {
        const values = py.toPy(data.values ?? {}),
          start = performance.now();
        try {
          await frame(debug(data.action, values), data.request, start);
        } finally {
          values.destroy();
        }
      }
    })
    .catch((error) =>
      scope.postMessage({
        type: "error",
        message: String(error),
        detail: error?.stack,
      }),
    );
};
