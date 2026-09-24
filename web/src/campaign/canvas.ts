/** Executes the original Cairo draw stream on a worker-owned 720p canvas.
 * Static surfaces stay cached. Only an ImageBitmap crosses to the UI thread.
 */
type Source = any[];
type Surface = {
  width: number;
  height: number;
  image: OffscreenCanvas | ImageBitmap;
  canvas?: OffscreenCanvas;
  ctx?: OffscreenCanvasRenderingContext2D;
  contextId?: number;
  version: number;
  asset?: string;
  depth: number;
};
type State = {
  surface: Surface;
  ctx: OffscreenCanvasRenderingContext2D;
  source: Source;
  rule: CanvasFillRule;
  stack: { source: Source; rule: CanvasFillRule }[];
  subpath: boolean;
  groups: {
    surface: Surface;
    ctx: OffscreenCanvasRenderingContext2D;
    source: Source;
    rule: CanvasFillRule;
    matrix: DOMMatrix;
  }[];
};
export class CanvasBackend {
  surfaces = new Map<number, Surface>();
  contexts = new Map<number, State>();
  groups = new Map<number, { image: OffscreenCanvas; matrix: DOMMatrix }>();
  private images = new Map<string, Promise<ImageBitmap>>();
  private reflected = new WeakMap<
    object,
    { version: number; image: OffscreenCanvas }
  >();
  private scratch: OffscreenCanvas[] = [];
  private scratchUsed = 0;
  readonly measure = new OffscreenCanvas(1, 1).getContext("2d")!;
  readonly root: string;
  constructor(root: string) {
    this.root = root;
  }
  private blank(width: number, height: number, opaque = false): Surface {
    const canvas = new OffscreenCanvas(width, height),
      ctx = canvas.getContext("2d")!;
    if (opaque) {
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, width, height);
    }
    ctx.imageSmoothingEnabled = true;
    return { width, height, image: canvas, canvas, ctx, version: 0, depth: 0 };
  }
  private temporary(width: number, height: number) {
    let canvas = this.scratch[this.scratchUsed++];
    if (!canvas) {
      canvas = new OffscreenCanvas(width, height);
      this.scratch.push(canvas);
    }
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    const ctx = canvas.getContext("2d")!;
    ctx.reset();
    return canvas;
  }
  pixels(id: number, data: any, width: number, height: number, format: number) {
    const lease = data instanceof Uint8Array ? null : data.getBuffer("u8");
    const bytes: Uint8Array = lease ? lease.data : data;
    const surface = this.blank(width, height),
      image = new ImageData(width, height),
      out = image.data;
    try {
      for (let i = 0; i < out.length; i += 4) {
        const a = format === 1 ? 255 : bytes[i + 3];
        const scale = a ? 255 / a : 0;
        out[i] = bytes[i + 2] * scale;
        out[i + 1] = bytes[i + 1] * scale;
        out[i + 2] = bytes[i] * scale;
        out[i + 3] = a;
      }
    } finally {
      lease?.release();
    }
    surface.ctx!.putImageData(image, 0, 0);
    this.surfaces.set(id, surface);
  }
  async execute(
    packet: { definitions: any[][]; commands: any[][]; releases: number[] },
    target: number,
  ) {
    // Source images are fetched only when their stage/cinematic actually uses them.
    await Promise.all(
      packet.definitions
        .filter((d) => d[3])
        .map(async (d) => {
          const url = this.root + d[3];
          let pending = this.images.get(url);
          if (!pending) {
            pending = fetch(url)
              .then((r) => {
                if (!r.ok) throw new Error(`Missing artwork: ${d[3]}`);
                return r.blob();
              })
              .then((b) => createImageBitmap(b));
            this.images.set(url, pending);
          }
          const image = await pending;
          this.surfaces.set(d[0], {
            width: d[1],
            height: d[2],
            image,
            asset: url,
            version: 0,
            depth: 0,
          });
        }),
    );
    for (const [id, w, h, asset, format] of packet.definitions)
      if (!asset && !this.surfaces.has(id))
        this.surfaces.set(id, this.blank(w, h, format === 1));
    this.scratchUsed = 0;
    for (const command of packet.commands) {
      if (command[0] === "context") {
        const [, id, surfaceId] = command,
          surface = this.surfaces.get(surfaceId)!;
        if (!surface.ctx)
          throw new Error("Cannot draw onto immutable source artwork");
        const ctx = surface.ctx;
        // Separate Cairo contexts share pixels, not graphics state.
        if (surface.contextId !== id) {
          while (surface.depth > 0) {
            ctx.restore();
            surface.depth--;
          }
          ctx.resetTransform();
          ctx.globalAlpha = 1;
          ctx.globalCompositeOperation = "source-over";
          ctx.fillStyle = "#000";
          ctx.strokeStyle = "#000";
          ctx.lineWidth = 2;
          ctx.lineCap = "butt";
          ctx.lineJoin = "miter";
          ctx.imageSmoothingEnabled = true;
          ctx.beginPath();
          ctx.save();
          surface.depth = 1;
          if (surface.contextId) this.contexts.delete(surface.contextId);
          surface.contextId = id;
        }
        this.contexts.set(id, {
          surface,
          ctx,
          source: ["color", [0, 0, 0, 1]],
          rule: "nonzero",
          stack: [],
          subpath: false,
          groups: [],
        });
        continue;
      }
      const [id, op, ...v] = command,
        s = this.contexts.get(id);
      if (!s) throw new Error(`Unknown drawing context ${id}`);
      const c = s.ctx;
      switch (op) {
        case "save":
          c.save();
          s.surface.depth++;
          s.stack.push({ source: s.source, rule: s.rule });
          break;
        case "restore":
          c.restore();
          s.surface.depth--;
          Object.assign(s, s.stack.pop());
          break;
        case "translate":
          c.translate(v[0], v[1]);
          break;
        case "scale":
          c.scale(v[0], v[1]);
          break;
        case "transform":
          c.transform(v[0], v[1], v[2], v[3], v[4], v[5]);
          break;
        case "source":
          s.source = v[0];
          break;
        case "move":
          c.moveTo(v[0], v[1]);
          break;
        case "line":
          c.lineTo(v[0], v[1]);
          break;
        case "curve":
          c.bezierCurveTo(v[0], v[1], v[2], v[3], v[4], v[5]);
          break;
        case "rect":
          c.rect(v[0], v[1], v[2], v[3]);
          break;
        case "arc":
          if (s.subpath) {
            c.moveTo(
              v[0] + v[2] * Math.cos(v[3]),
              v[1] + v[2] * Math.sin(v[3]),
            );
            s.subpath = false;
          }
          c.arc(v[0], v[1], Math.max(0, v[2]), v[3], v[4]);
          break;
        case "close":
          c.closePath();
          break;
        case "begin":
          c.beginPath();
          s.subpath = false;
          break;
        case "subpath":
          s.subpath = true;
          break;
        case "clip":
          c.clip(s.rule);
          c.beginPath();
          break;
        case "fillRule":
          s.rule = v[0];
          break;
        case "operator":
          c.globalCompositeOperation = v[0];
          break;
        case "lineWidth":
          if (v[0] > 0) c.lineWidth = v[0];
          break;
        case "lineCap":
          c.lineCap = v[0];
          break;
        case "lineJoin":
          c.lineJoin = v[0];
          break;
        case "antialias":
          break;
        case "font":
          c.font = `${v[2] ? "bold " : ""}${v[1]}px ${v[0]}`;
          break;
        case "blit": {
          const [sid, frame, x, y, w, h, flip, alpha] = v,
            source = this.surfaces.get(sid)!;
          c.save();
          c.globalAlpha *= Math.min(1, alpha);
          c.imageSmoothingEnabled = false;
          c.translate(x, y);
          if (flip) {
            c.translate(w, 0);
            c.scale(-1, 1);
          }
          c.drawImage(
            source.image,
            frame[0],
            frame[1],
            frame[2],
            frame[3],
            0,
            0,
            w,
            h,
          );
          c.restore();
          c.beginPath();
          s.surface.version++;
          break;
        }
        case "patternRect": {
          const [source, x, y, w, h] = v,
            surface = this.surfaces.get(source[1])!,
            image = surface.image,
            sw = surface.width,
            sh = surface.height;
          const axis = (value: number, size: number) => {
            const period = source[3] === 2 ? size * 2 : size;
            const p = ((value % period) + period) % period;
            return p < size
              ? { position: p, room: size - p, flip: false }
              : {
                  position: period - p,
                  room: p - size ? period - p : size,
                  flip: true,
                };
          };
          c.save();
          c.imageSmoothingEnabled = source[4] !== 0;
          let yy = 0;
          while (yy < h) {
            const sy = axis(y + yy + source[2][5], sh),
              dh = Math.min(h - yy, sy.room);
            let xx = 0;
            while (xx < w) {
              const sx = axis(x + xx + source[2][4], sw),
                dw = Math.min(w - xx, sx.room);
              c.save();
              c.translate(
                x + xx + (sx.flip ? dw : 0),
                y + yy + (sy.flip ? dh : 0),
              );
              c.scale(sx.flip ? -1 : 1, sy.flip ? -1 : 1);
              c.drawImage(
                image,
                sx.position - (sx.flip ? dw : 0),
                sy.position - (sy.flip ? dh : 0),
                dw,
                dh,
                0,
                0,
                dw,
                dh,
              );
              c.restore();
              xx += dw;
            }
            yy += dh;
          }
          c.restore();
          c.beginPath();
          s.surface.version++;
          break;
        }
        case "fill":
          c.fillStyle = this.brush(s.source, c);
          c.fill(s.rule);
          c.beginPath();
          s.surface.version++;
          break;
        case "stroke":
        case "strokeKeep":
          c.strokeStyle = this.brush(s.source, c);
          c.stroke();
          if (op === "stroke") c.beginPath();
          s.surface.version++;
          break;
        case "paint":
          this.paint(s.source, c, v[0]);
          s.surface.version++;
          break;
        case "text":
          c.fillStyle = this.brush(s.source, c);
          c.fillText(v[0], v[1], v[2]);
          s.surface.version++;
          break;
        case "pushGroup": {
          const matrix = c.getTransform(),
            canvas = this.temporary(s.surface.width, s.surface.height),
            gc = canvas.getContext("2d")!;
          this.copyStyle(c, gc);
          gc.setTransform(matrix);
          s.groups.push({
            surface: s.surface,
            ctx: c,
            source: s.source,
            rule: s.rule,
            matrix,
          });
          s.surface = {
            width: canvas.width,
            height: canvas.height,
            image: canvas,
            canvas,
            ctx: gc,
            version: 0,
            depth: 0,
          };
          s.ctx = gc;
          break;
        }
        case "popGroup": {
          const group = s.groups.pop()!;
          this.groups.set(v[0], {
            image: s.surface.canvas!,
            matrix: group.matrix,
          });
          s.surface = group.surface;
          s.ctx = group.ctx;
          s.rule = group.rule;
          s.source = ["group", v[0]];
          break;
        }
        case "mask": {
          const matrix = c.getTransform(),
            canvas = this.temporary(s.surface.width, s.surface.height),
            mc = canvas.getContext("2d")!;
          mc.setTransform(matrix);
          this.paint(s.source, mc, 1);
          mc.globalCompositeOperation = "destination-in";
          this.paint(v[0], mc, 1);
          c.save();
          c.resetTransform();
          c.drawImage(canvas, 0, 0);
          c.restore();
          s.surface.version++;
          break;
        }
        default:
          throw new Error(`Unsupported Cairo operation ${op}`);
      }
    }
    const out = this.surfaces.get(target);
    if (!out?.canvas) throw new Error("Missing output surface");
    const bitmap = out.canvas.transferToImageBitmap(); // consumes only the output; next frame paints black first
    this.groups.clear();
    for (const id of packet.releases) {
      const old = this.surfaces.get(id);
      if (old?.contextId) this.contexts.delete(old.contextId);
      this.surfaces.delete(id);
    }
    // Close decoded images once no live native surface references them. This also
    // makes native LRU cache eviction release browser texture memory.
    const active = new Set(
      [...this.surfaces.values()].map((s) => s.asset).filter(Boolean),
    );
    for (const [url, p] of this.images)
      if (!active.has(url)) {
        void p.then((image) => image.close());
        this.images.delete(url);
      }
    return bitmap;
  }
  private copyStyle(
    from: OffscreenCanvasRenderingContext2D,
    to: OffscreenCanvasRenderingContext2D,
  ) {
    to.globalAlpha = from.globalAlpha;
    to.globalCompositeOperation = from.globalCompositeOperation;
    to.lineWidth = from.lineWidth;
    to.lineCap = from.lineCap;
    to.lineJoin = from.lineJoin;
    to.font = from.font;
    to.imageSmoothingEnabled = from.imageSmoothingEnabled;
  }
  private brush(
    source: Source,
    c: OffscreenCanvasRenderingContext2D,
  ): string | CanvasGradient | CanvasPattern {
    if (source[0] === "color") {
      const [r, g, b, a] = source[1];
      return `rgba(${r * 255},${g * 255},${b * 255},${Math.max(0, Math.min(1, a))})`;
    }
    if (source[0] === "linear" || source[0] === "radial") {
      const a = source[1];
      const gradient =
        source[0] === "linear"
          ? c.createLinearGradient(a[0], a[1], a[2], a[3])
          : c.createRadialGradient(
              a[0],
              a[1],
              Math.max(0, a[2]),
              a[3],
              a[4],
              Math.max(0, a[5]),
            );
      for (const [p, r, g, b, alpha] of source[2])
        gradient.addColorStop(
          Math.max(0, Math.min(1, p)),
          `rgba(${r * 255},${g * 255},${b * 255},${Math.max(0, Math.min(1, alpha))})`,
        );
      return gradient;
    }
    if (source[0] === "group") {
      const group = this.groups.get(source[1])!,
        pattern = c.createPattern(group.image, "no-repeat")!;
      pattern.setTransform(group.matrix.inverse());
      return pattern;
    }
    const pattern = c.createPattern(
      this.patternImage(source),
      source[3] ? "repeat" : "no-repeat",
    )!;
    pattern.setTransform(new DOMMatrix(source[2]).inverse());
    c.imageSmoothingEnabled = source[4] !== 0;
    return pattern;
  }
  private patternImage(source: Source) {
    const surface = this.surfaces.get(source[1]);
    if (!surface) throw new Error(`Missing source surface ${source[1]}`);
    let image = surface.image;
    if (source[3] === 2) {
      let reflected = this.reflected.get(image);
      if (!reflected || reflected.version !== surface.version) {
        const canvas =
            reflected?.image ??
            new OffscreenCanvas(surface.width * 2, surface.height * 2),
          ctx = canvas.getContext("2d")!;
        ctx.reset();
        ctx.drawImage(image, 0, 0);
        ctx.save();
        ctx.translate(surface.width * 2, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(image, 0, 0);
        ctx.restore();
        ctx.save();
        ctx.translate(0, surface.height * 2);
        ctx.scale(1, -1);
        ctx.drawImage(
          canvas,
          0,
          0,
          surface.width * 2,
          surface.height,
          0,
          0,
          surface.width * 2,
          surface.height,
        );
        ctx.restore();
        reflected = { version: surface.version, image: canvas };
        this.reflected.set(image, reflected);
      }
      image = reflected.image;
    }
    return image;
  }

  private paint(
    source: Source,
    c: OffscreenCanvasRenderingContext2D,
    alpha: number,
  ) {
    c.save();
    c.globalAlpha *= Math.max(0, Math.min(1, alpha));
    if (source[0] === "surface" && source[3] === 0) {
      const surface = this.surfaces.get(source[1]);
      if (!surface) throw new Error(`Missing paint surface ${source[1]}`);
      const m = new DOMMatrix(source[2]).inverse();
      c.transform(m.a, m.b, m.c, m.d, m.e, m.f);
      c.imageSmoothingEnabled = source[4] !== 0;
      c.drawImage(surface.image, 0, 0);
    } else if (source[0] === "group") {
      const group = this.groups.get(source[1])!;
      const m = group.matrix.inverse();
      c.transform(m.a, m.b, m.c, m.d, m.e, m.f);
      c.drawImage(group.image, 0, 0);
    } else {
      c.fillStyle = this.brush(source, c);
      const inv = c.getTransform().inverse();
      const points = [
        [0, 0],
        [c.canvas.width, 0],
        [0, c.canvas.height],
        [c.canvas.width, c.canvas.height],
      ].map(([x, y]) => inv.transformPoint({ x, y }));
      const xs = points.map((p) => p.x),
        ys = points.map((p) => p.y);
      c.fillRect(
        Math.min(...xs),
        Math.min(...ys),
        Math.max(...xs) - Math.min(...xs),
        Math.max(...ys) - Math.min(...ys),
      );
    }
    c.restore();
  }
  get memoryBytes() {
    let total = 0;
    for (const s of this.surfaces.values()) total += s.width * s.height * 4;
    return total;
  }
}
