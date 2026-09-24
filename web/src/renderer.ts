import {
  Application,
  Assets,
  Container,
  Rectangle,
  Sprite,
  Texture,
} from "pixi.js";
import { Fight, FLOOR, band, type Wave } from "./fight";
export interface Manifest {
  pages: string[];
  frames: Record<string, { page: number; rect: number[] }>;
  audio: Record<string, string>;
  music: string;
}
/** A reusable sprite batch. No per-frame vector tessellation or texture uploads. */
export class Scene {
  readonly app = new Application();
  readonly layer = new Container();
  readonly textures = new Map<string, Texture>();
  private pool: Sprite[] = [];
  private used = 0;
  async init(
    host: HTMLElement,
    manifest: Manifest,
    progress: (value: string) => void,
  ) {
    await this.app.init({
      width: 1280,
      height: 720,
      resolution: 1,
      preference: "webgl",
      antialias: false,
      autoStart: false,
      backgroundColor: 0x080b0a,
    });
    this.app.stage.eventMode = "none";
    host.prepend(this.app.canvas);
    this.app.canvas.setAttribute("aria-label", "Omacontra Reaper encounter");
    const pages: Texture[] = [];
    for (let i = 0; i < manifest.pages.length; i++) {
      progress(`LOADING ART ${i + 1} / ${manifest.pages.length}`);
      const t = await Assets.load<Texture>(`game/${manifest.pages[i]}`);
      t.source.scaleMode = "nearest";
      pages.push(t);
    }
    for (const [key, { page, rect }] of Object.entries(manifest.frames))
      this.textures.set(
        key,
        new Texture({
          source: pages[page].source,
          frame: new Rectangle(...(rect as [number, number, number, number])),
        }),
      );
    const bg = await Assets.load<Texture>("game/arena.png");
    bg.source.scaleMode = "nearest";
    this.textures.set("arena", bg);
    // Cache effect slices once, never create subtextures inside the render loop.
    const wave = this.textures.get("wave")!;
    for (let i = 0; i < 16; i++)
      this.textures.set(
        `wave${i}`,
        new Texture({
          source: wave.source,
          frame: new Rectangle(
            wave.frame.x + (i * wave.width) / 16,
            wave.frame.y,
            wave.width / 16,
            wave.height,
          ),
        }),
      );
    for (let pose = 0; pose < 3; pose++) {
      const t = this.textures.get(`boss${pose}`)!;
      for (let row = 0; row < 7; row++)
        for (let col = 0; col < 5; col++)
          this.textures.set(
            `shard${pose}-${row}-${col}`,
            new Texture({
              source: t.source,
              frame: new Rectangle(
                t.frame.x + (col * t.width) / 5,
                t.frame.y + (row * t.height) / 7,
                t.width / 5,
                t.height / 7,
              ),
            }),
          );
    }
    this.app.stage.addChild(this.layer);
  }
  sprite(
    key: string,
    x: number,
    y: number,
    w: number,
    h: number,
    alpha = 1,
    rotation = 0,
    tint = 0xffffff,
    flip = false,
    anchorX = 0.5,
    anchorY = 0.5,
  ) {
    if (alpha <= 0 || w <= 0 || h <= 0) return;
    let s = this.pool[this.used];
    if (!s) {
      s = new Sprite();
      this.pool.push(s);
      this.layer.addChild(s);
    }
    this.used++;
    s.visible = true;
    s.texture = key === "white" ? Texture.WHITE : this.textures.get(key)!;
    s.anchor.set(anchorX, anchorY);
    s.position.set(x, y);
    s.width = w;
    s.height = h;
    if (flip) s.scale.x *= -1;
    s.rotation = rotation;
    s.alpha = alpha;
    s.tint = tint;
    return s;
  }
  glow(x: number, y: number, size: number, color: number, alpha: number) {
    this.sprite("glow", x, y, size, size, alpha, 0, color);
  }
  draw(f: Fight, interpolation: number) {
    this.used = 0;
    this.sprite("arena", 640, 360, 1280, 720);
    // Subtle dust and machinery lights: pre-uploaded stamps, bounded fill rate.
    const decorative = f.effectsScale < 1 ? 8 : 20;
    for (let i = 0; i < decorative; i++) {
      const x = (i * 137.9 + Math.sin(f.clock * 0.14 + i) * 24) % 1280,
        y = (i * 61 + f.clock * (6 + (i % 4))) % FLOOR;
      this.sprite(
        "white",
        x,
        y,
        (i % 3) + 1,
        2,
        0.1 + 0.1 * Math.sin(f.clock + i),
        0,
        0xc4ba93,
      );
    }
    for (const [x, y] of [
      [802, 145],
      [1220, 495],
      [336, 333],
    ])
      this.glow(x, y, 65, 0xef3a16, 0.1 + 0.035 * Math.sin(f.clock * 2));
    const [dx, dy] = f.bossOffset,
      pose = f.state === "dying" ? f.deathPose : f.bossPose;
    const [bw, bh] = [
      [492, 570],
      [468, 590],
      [550, 439],
    ][pose].map((v) => v * 0.96);
    const left = 1280 * 0.57 + dx,
      top = FLOOR - bh + dy;
    if (f.state !== "won") {
      if (f.state !== "dying")
        this.sprite(
          `boss${pose}`,
          left,
          top,
          bw,
          bh,
          1,
          0,
          0xffffff,
          false,
          0,
          0,
        );
      else {
        this.sprite(
          `boss${pose}`,
          left + Math.sin(f.deathAge * 38) * 6,
          top,
          bw,
          bh,
          Math.max(0, 1 - f.deathAge / 2),
          0,
          0xffffff,
          false,
          0,
          0,
        );
        const t = Math.max(0, f.deathAge - 0.8);
        if (t)
          for (let row = 0; row < 7; row++)
            for (let col = 0; col < 5; col++) {
              const i = row * 5 + col;
              this.sprite(
                `shard${pose}-${row}-${col}`,
                left + ((col + 0.5) * bw) / 5 + Math.sin(i * 2.39) * 170 * t,
                Math.min(
                  FLOOR - 10,
                  top +
                    ((row + 0.5) * bh) / 7 +
                    (-100 - ((i * 37) % 150)) * t +
                    170 * t * t,
                ),
                bw / 5,
                bh / 7,
                Math.max(0, Math.min(1, (4 - f.deathAge) * 0.7)),
                Math.sin(i) * t * 3,
              );
            }
      }
    }
    if (f.state === "play") {
      const [x, y] = f.body;
      this.glow(
        x,
        y,
        180,
        f.shielded ? 0xec3023 : 0xffc163,
        0.18 + 0.08 * Math.sin(f.clock * 3),
      );
      this.glow(
        x,
        y,
        f.shielded ? 27 : 52,
        f.shielded ? 0xff3129 : 0xffe6aa,
        0.7,
      );
      if (!f.shielded)
        this.sprite("impact", x, y, 36, 36, 0.65 + 0.2 * Math.sin(f.clock * 8));
      if (f.bossFlash) this.sprite("impact", x, y, 65, 65, 0.9);
    }
    for (const role of ["eye", "raven"] as const) {
      if (!f.nodes[role]) continue;
      const [x, y] = f.nodeCenter(role),
        charging = f.warning === (role === "eye" ? "aimed" : "raven");
      this.glow(x, y, charging ? 150 : 110, 0xff3523, charging ? 0.5 : 0.25);
      this.sprite(
        role === "eye" ? "eye" : `raven${Math.floor(f.clock * 7) % 3}`,
        x,
        y,
        80,
        78,
        1,
        charging
          ? 0
          : (role === "raven" ? 0.16 : 0.07) * Math.sin(f.patrol[role] * 1.2),
      );
      this.sprite(
        "white",
        x - 35,
        y + 47,
        (70 * f.nodes[role]) / f.nodeMax,
        3,
        1,
        0,
        0xf83124,
        false,
        0,
        0,
      );
      if (f.nodeFire[role])
        this.sprite("impact", x, y, 70, 70, f.nodeFire[role] / 0.2);
      if (f.nodeFlash[role]) this.sprite("impact", x, y, 40, 40);
    }
    if (f.warning === "scythe") {
      const [top, bottom] = band(f.pattern[0]);
      this.sprite(
        "white",
        640,
        (top + bottom) / 2,
        1280,
        bottom - top,
        0.035 + 0.025 * Math.sin(f.clock * 12),
        0,
        0xff3322,
      );
    }
    for (const b of f.shots) {
      if (b.life <= 0) continue;
      const x = b.px + (b.x - b.px) * interpolation,
        y = b.py + (b.y - b.py) * interpolation;
      if (b.kind.startsWith("scythe_")) {
        const kind = b.kind.slice(7) as Wave,
          [top, bottom] = band(kind),
          height = bottom - top;
        for (let i = 0; i < 16; i++) {
          const offset = Math.sin(f.clock * 10 - i * 0.65);
          if (kind === "dash")
            this.sprite(
              `wave${i}`,
              x - 150 + ((i + 0.5) * 300) / 16,
              (top + bottom) / 2 + offset * height * 0.035,
              300 / 16 + 0.2,
              height * 0.92,
            );
          else
            this.sprite(
              `wave${i}`,
              x + offset * 70 * 0.035,
              top + ((i + 0.5) * height) / 16,
              height / 16 + 0.2,
              70 * 0.92,
              1,
              Math.PI / 2,
            );
        }
      } else if (b.enemy) {
        const angle = Math.atan2(b.vy, b.vx);
        this.glow(x, y, b.kind === "raven" ? 70 : 74, 0xff3523, 0.3);
        if (b.kind === "raven") {
          const frame = `raven${Math.floor(f.clock * 11) % 3}`;
          for (let i = 3; i >= 1; i--)
            this.sprite(
              frame,
              x - Math.cos(angle) * i * 13,
              y - Math.sin(angle) * i * 13,
              52,
              48,
              0.07 * (4 - i),
              0,
              0xffffff,
              b.vx > 0,
            );
          this.sprite(frame, x, y, 52, 48, 1, 0, 0xffffff, b.vx > 0);
        } else {
          this.sprite(
            "white",
            x - Math.cos(angle) * 15,
            y - Math.sin(angle) * 15,
            30,
            3,
            0.65,
            angle,
            0xffaa33,
          );
          this.sprite("skull", x, y, 46, 42, 1, 0, 0xffffff, b.vx > 0);
        }
      } else {
        const angle = Math.atan2(b.vy, b.vx);
        this.sprite("white", x, y, 22, 4, 0.7, angle, 0xff861b);
        this.sprite(
          "white",
          x + Math.cos(angle) * 3,
          y + Math.sin(angle) * 3,
          14,
          2,
          1,
          angle,
          0xfff4c0,
        );
      }
    }
    for (const p of f.particles)
      if (p.dust) {
        const age = 1 - p.life / p.maxLife,
          size = p.size * (0.65 + age * 0.8);
        this.sprite(
          "dust",
          p.x,
          p.y - size * 0.2,
          size,
          (size * 20) / 32,
          (1 - age) ** 1.5,
        );
      }
    const x = f.previousX + (f.x - f.previousX) * interpolation,
      y = f.previousY + (f.y - f.previousY) * interpolation;
    if (f.state !== "dead")
      this.sprite(
        "glow",
        x,
        FLOOR,
        Math.max(10, 38 - (FLOOR - y) * 0.06),
        7,
        0.5,
        0,
        0x000000,
      );
    this.hero(f, x, y);
    for (const p of f.particles)
      if (!p.dust)
        this.sprite(
          "white",
          p.x,
          p.y,
          p.size,
          p.size,
          Math.min(1, p.life * 4),
          0,
          p.color,
        );
    this.sprite("white", 640, FLOOR, 1280, 2, 0.7, 0, 0xd9d1a6);
    for (let i = this.used; i < this.pool.length; i++)
      this.pool[i].visible = false;
    this.app.render();
  }
  private hero(f: Fight, x: number, y: number) {
    if (f.hitAge !== null) {
      const t = f.hitAge;
      this.sprite(
        "jump",
        f.hitOrigin[0] - f.hitFacing * 110 * t,
        f.hitOrigin[1] - 40 - 210 * t + 430 * t * t,
        128,
        112,
        clamp01((0.55 - t) / 0.12),
        -f.hitFacing * (0.35 + t * 3.5),
        0xffffff,
        f.hitFacing < 0,
        0.5,
        0.62,
      );
      return;
    }
    if (f.state === "dead") return;
    const alpha = f.invuln > 0 && Math.floor(f.clock * 14) % 2 ? 0.45 : 1;
    const running = f.moving && !f.duck && !f.sliding && f.y >= FLOOR - 1;
    const carry = running && !f.aim && !f.shootHeld && !f.muzzle;
    const key = f.sliding
      ? "slide"
      : f.duck
        ? "duck"
        : f.y < FLOOR - 1
          ? "jump"
          : running
            ? `${carry ? "runcarry" : f.runDirection === f.facing ? "runfire" : "runback"}${f.runFrame}`
            : "stand";
    this.sprite(
      key,
      x,
      y,
      128,
      112,
      alpha,
      0,
      0xffffff,
      f.facing < 0,
      0.5,
      96 / 112,
    );
    if (!carry) {
      const [wx, wy, angle] = f.weaponPose();
      const s = this.sprite(
        "weapon",
        wx + x - f.x,
        wy + y - f.y,
        1536 * 0.035,
        530 * 0.035,
        alpha,
        angle,
        0xffffff,
        false,
        180 / 1536,
        170 / 530,
      );
      if (s && f.facing < 0) s.scale.y *= -1;
      if (f.muzzle) {
        const mx = wx + x - f.x + Math.cos(angle) * 45.85,
          my = wy + y - f.y + Math.sin(angle) * 45.85;
        this.glow(mx, my, 28, 0xffb531, 0.6);
        this.sprite("white", mx, my, 10, 3, alpha, angle, 0xfff7d2);
      }
    }
  }
  get spriteCount() {
    return this.used;
  }
}
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
