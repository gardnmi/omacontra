/** Reaper simulation ported from stages/reaper/combat.py (v1.0.2).
 * World coordinates, collision bands and timings intentionally match desktop.
 * No browser/rendering dependencies; deterministic combat tests run in Node.
 */
export const W = 1280,
  H = 720,
  FLOOR = 693,
  STEP = 1 / 60;
export type Point = [number, number];
export type Wave = "dash" | "double" | "high" | "low";
export type Attack = "aimed" | "raven" | "scythe";
export const PATTERNS: Wave[][] = [
  ["dash"],
  ["double"],
  ["high"],
  ["low", "high", "low"],
  ["dash", "dash"],
];
export const CUES = {
  dash: "AIR DASH",
  double: "DOUBLE JUMP",
  high: "SLIDE",
  low: "JUMP",
};
export interface Controls {
  move?: number;
  jump?: boolean;
  duck?: boolean;
  shoot?: boolean;
  aim?: Point | null;
  aimUp?: boolean;
  slide?: boolean;
  slidePressed?: boolean;
}
export const clamp = (n: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, n));
export function band(kind: Wave): Point {
  return kind === "high"
    ? [FLOOR - 250, FLOOR - 49]
    : [FLOOR - (kind === "double" ? 140 : 68), FLOOR];
}
export function segmentHit(
  ax: number,
  ay: number,
  bx: number,
  by: number,
  x: number,
  y: number,
  r: number,
) {
  const dx = bx - ax,
    dy = by - ay,
    u = clamp(
      ((x - ax) * dx + (y - ay) * dy) / Math.max(0.001, dx * dx + dy * dy),
      0,
      1,
    );
  return (ax + u * dx - x) ** 2 + (ay + u * dy - y) ** 2 <= r * r;
}
export function segmentBox(
  ax: number,
  ay: number,
  bx: number,
  by: number,
  box: number[],
) {
  let lo = 0,
    hi = 1;
  for (const [start, delta, mn, mx] of [
    [ax, bx - ax, box[0], box[2]],
    [ay, by - ay, box[1], box[3]],
  ]) {
    if (Math.abs(delta) < 1e-9) {
      if (!(mn <= start && start <= mx)) return false;
    } else {
      const a = (mn - start) / delta,
        b = (mx - start) / delta;
      lo = Math.max(lo, Math.min(a, b));
      hi = Math.min(hi, Math.max(a, b));
      if (lo > hi) return false;
    }
  }
  return true;
}
export class Shot {
  x = 0;
  y = 0;
  px = 0;
  py = 0;
  vx = 0;
  vy = 0;
  enemy = false;
  life = 2;
  kind = "bullet";
  damage = 1;
}
export class Particle {
  x = 0;
  y = 0;
  vx = 0;
  vy = 0;
  life = 0;
  maxLife = 0;
  color = 0;
  size = 3;
  dust = false;
}
export class Fight {
  hp = 5;
  bossHp = 180;
  bossMax = 180;
  state: "play" | "dead" | "dying" | "won" = "play";
  x = 180;
  y = FLOOR;
  previousX = 180;
  previousY = FLOOR;
  vy = 0;
  facing = 1;
  duck = false;
  moving = false;
  clock = 0;
  fire = 0;
  invuln = 2;
  runPhase = 0;
  runDirection = 1;
  wasRunning = false;
  nodes = { eye: 12, raven: 12 };
  nodeMax = 12;
  exposed = 0;
  attackTimer = 2;
  warning: Attack | null = null;
  warningTime = 0;
  attackNumber = 0;
  swingTime = 0;
  notice = "THE WALLPAPER IS AWAKE";
  noticeTime = 3;
  nodeFlash = { eye: 0, raven: 0 };
  nodeFire = { eye: 0, raven: 0 };
  bossFlash = 0;
  muzzle = 0;
  wasJump = false;
  jumpsUsed = 0;
  jumpFlash = 0;
  slideTime = 0;
  slideCooldown = 0;
  slideDirection = 1;
  slideBuffer = 0;
  wasSlide = false;
  dashTime = 0;
  dashUsed = false;
  dashDirection = 1;
  dashCasts = 0;
  shootHeld = false;
  shotsFired = 0;
  aim: Point | null = null;
  volleyTarget: Point | null = null;
  patrol = { eye: 0, raven: 0 };
  bossMotion = 0;
  scytheRound = 0;
  pattern: Wave[] = [];
  waveQueue: [number, Wave][] = [];
  waveClock = 0;
  burstQueue: [number, Attack][] = [];
  deathAge = 0;
  deathPose = 0;
  deathOffset: Point = [0, 0];
  deathBlastTimer = 0;
  shots: Shot[] = [];
  private shotPool: Shot[] = [];
  particles: Particle[] = [];
  private particlePool: Particle[] = [];
  events: string[] = [];
  lastSound = new Map<string, number>();
  hitAge: number | null = null;
  hitOrigin: Point = [180, FLOOR];
  hitFacing = 1;
  respawnAnchor: Point = [180, FLOOR];
  damageTaken = 0;
  damageClock = -99;
  unlimited = false;
  landingAge = 0;
  brakeAge = 0;
  dustTimer = 0;
  effectsScale = 1;
  get phase() {
    return this.bossHp > 120 ? 1 : this.bossHp > 60 ? 2 : 3;
  }
  get shielded() {
    return this.nodes.eye > 0 || this.nodes.raven > 0;
  }
  get sliding() {
    return this.slideTime > 0;
  }
  get bossPose() {
    return this.warning === "scythe" ? 1 : this.swingTime > 0 ? 2 : 0;
  }
  get bossOffset(): Point {
    if (this.state === "dying" || this.state === "won") return this.deathOffset;
    const windup =
      this.warning === "scythe" ? Math.max(0, 1 - this.warningTime / 1.5) : 0;
    return [
      Math.sin(this.bossMotion * 0.65) * 38 -
        Math.max(windup, this.swingTime / 0.65) * 28,
      -Math.abs(Math.sin(this.bossMotion * 0.85)) * 10,
    ];
  }
  get body(): Point {
    const [hx, hy, bh] = [
        [180, 215, 570],
        [227, 245, 590],
        [385, 105, 439],
      ][this.bossPose],
      [dx, dy] = this.bossOffset;
    return [W * 0.57 + hx * 0.96 + dx, FLOOR - bh * 0.96 + hy * 0.96 + dy];
  }
  get center(): Point {
    return [
      this.x,
      this.y -
        (this.sliding ? 32 : this.duck ? 43 : this.y < FLOOR - 1 ? 35 : 52),
    ];
  }
  get hitbox() {
    const height = this.sliding
        ? 40
        : this.duck
          ? 59
          : this.y < FLOOR - 1
            ? 60
            : 77,
      half = this.sliding ? 24 : 14;
    return [this.x - half, this.y - height, this.x + half, this.y - 3];
  }
  nodeCenter(role: "eye" | "raven"): Point {
    const t = this.patrol[role];
    return role === "eye"
      ? [525 + 115 * Math.sin(t * 0.65), 225 + 52 * Math.sin(t * 1.1)]
      : [1105 - 190 * Math.sin(t * 0.4) ** 2, 130 + 35 * Math.sin(t * 1.25)];
  }
  get runFrame() {
    const phase =
      (((this.runDirection === this.facing ? this.runPhase : -this.runPhase) %
        6) +
        6) %
      6;
    return [1.2, 2.4, 3, 4.2, 5.4, 6].findIndex((end) => phase < end);
  }
  weaponPose(): [number, number, number] {
    const index = this.duck || this.sliding ? 5 : this.y < FLOOR - 1 ? 4 : 0;
    const [sw, sh, anchor, sx, sy] =
      index === 5
        ? [355, 310, 31.6, 110, 100]
        : index === 4
          ? [275, 317, 23, 85, 100]
          : [305, 409, 25, 90, 110];
    const width = sw * 0.2;
    let height = sh * 0.2 * (this.sliding ? 0.75 : 1);
    if (this.y >= FLOOR - 1 && !this.moving)
      height *= 1 - 0.04 * Math.sin((Math.PI * this.landingAge) / 0.18);
    let left = this.x - (this.facing > 0 ? anchor : width - anchor),
      top = this.y - height;
    if (index === 0 && this.moving && this.y >= FLOOR - 1) {
      left += this.runDirection * 1.5;
      top +=
        [0, -0.5, 2, 0, -0.5, 2][this.runFrame] +
        2 * Math.sin((Math.PI * this.landingAge) / 0.18);
    }
    const x = left + (this.facing > 0 ? sx * 0.2 : width - sx * 0.2),
      y = top + (sy * height) / sh;
    return [
      x,
      y,
      this.aim
        ? Math.atan2(this.aim[1] - y, this.aim[0] - x)
        : this.facing > 0
          ? 0
          : Math.PI,
    ];
  }
  sound(name: string, cooldown = 0) {
    if (this.clock - (this.lastSound.get(name) ?? -999) < cooldown) return;
    this.lastSound.set(name, this.clock);
    if (this.events.length < 32) this.events.push(name);
  }
  spawn(
    x: number,
    y: number,
    vx: number,
    vy: number,
    enemy = false,
    kind = "bullet",
    life = 2,
  ) {
    const b = this.shotPool.pop() ?? new Shot();
    Object.assign(b, {
      x,
      y,
      px: x,
      py: y,
      vx,
      vy,
      enemy,
      kind,
      life,
      damage: 1,
    });
    this.shots.push(b);
    return b;
  }
  particle(
    x: number,
    y: number,
    vx: number,
    vy: number,
    life: number,
    color: number,
    size = 3,
    dust = false,
  ) {
    if (this.particles.length >= 300 * this.effectsScale) return;
    const p = this.particlePool.pop() ?? new Particle();
    Object.assign(p, { x, y, vx, vy, life, maxLife: life, color, size, dust });
    this.particles.push(p);
  }
  burst(x: number, y: number, color: number, count = 18) {
    for (let i = 0; i < count * this.effectsScale; i++) {
      const a = Math.random() * Math.PI * 2,
        v = 20 + Math.random() * 120;
      this.particle(
        x,
        y,
        Math.cos(a) * v,
        Math.sin(a) * v,
        0.2 + Math.random() * 0.6,
        color,
      );
    }
  }
  hurt() {
    if (this.invuln > 0 || this.state !== "play") return;
    this.damageTaken++;
    this.damageClock = this.clock;
    if (!this.unlimited) this.hp--;
    this.burst(...this.center, 0xf53020, 22);
    this.hitAge = 0;
    this.hitOrigin = [this.x, this.y];
    this.hitFacing = this.facing;
    this.invuln = 3.55;
    this.muzzle = this.slideTime = this.dashTime = this.vy = 0;
    this.moving = false;
    this.sound(this.hp <= 0 ? "player_death" : "hurt");
    if (this.hp <= 0) {
      this.state = "dead";
      this.notice = "DHH DOWN";
      this.noticeTime = 999;
    }
  }
  hitTarget(ax: number, ay: number, bx: number, by: number, damage = 1) {
    if (this.state !== "play") return false;
    const hits: {
      distance: number;
      role: "eye" | "raven" | "boss";
      x: number;
      y: number;
    }[] = [];
    for (const role of ["eye", "raven"] as const) {
      const [x, y] = this.nodeCenter(role);
      if (this.nodes[role] > 0 && segmentHit(ax, ay, bx, by, x, y, 46.8))
        hits.push({ distance: Math.hypot(x - ax, y - ay), role, x, y });
    }
    const [cx, cy] = this.body;
    if (segmentHit(ax, ay, bx, by, cx, cy, 75))
      hits.push({
        distance: Math.hypot(cx - ax, cy - ay),
        role: "boss",
        x: cx,
        y: cy,
      });
    hits.sort((a, b) => a.distance - b.distance);
    if (!hits.length) return false;
    const { role, x, y } = hits[0];
    if (role === "boss") {
      this.sound(this.shielded ? "armor" : "impact");
      this.burst(x, y, this.shielded ? 0xd9d1a6 : 0xffaa33, 9);
      if (!this.shielded) {
        this.bossHp = Math.max(0, this.bossHp - damage);
        this.bossFlash = 0.08;
        if (!this.bossHp) {
          this.sound("rupture");
          this.deathPose = this.bossPose;
          this.deathOffset = this.bossOffset;
          this.state = "dying";
          this.deathAge = 0;
          this.waveQueue.length = this.burstQueue.length = 0;
          this.warning = null;
          this.muzzle = this.bossFlash = 0;
          for (const b of this.shots) b.life = 0;
          this.notice = "CORE RUPTURE";
          this.noticeTime = 999;
          this.burst(x, y, 0xffaa33, 65);
        }
      }
    } else {
      if (this.nodes[role] > damage)
        this.sound(role === "raven" ? "raven_hit" : "eye_hit");
      this.nodes[role] = Math.max(0, this.nodes[role] - damage);
      this.nodeFlash[role] = 0.1;
      this.burst(x, y, 0xffaa33, 9);
      if (!this.nodes[role]) {
        this.sound(role === "raven" ? "raven_break" : "eye_break");
        this.burst(x, y, 0xff3322, 35);
        if (!this.shielded) {
          this.sound("expose");
          this.exposed = 11;
          this.notice = "CORE EXPOSED / HIT THE REAPER";
          this.noticeTime = 3;
        }
      }
    }
    return true;
  }
  prepareScythe() {
    this.pattern = PATTERNS[this.scytheRound++ % PATTERNS.length];
  }
  launchWave(kind: Wave) {
    this.sound("sweep");
    this.swingTime = 0.65;
    const x = W * 0.63 + this.bossOffset[0],
      [top, bottom] = band(kind);
    const speed =
      kind === "dash"
        ? this.dashCasts === 0
          ? 200
          : 280
        : 380 + this.phase * 15;
    if (kind === "dash") this.dashCasts++;
    this.spawn(x, (top + bottom) / 2, -speed, 0, true, `scythe_${kind}`, 7);
    this.burst(x, (top + bottom) / 2, 0xff3322, 35);
    this.notice = this.pattern.map((p) => CUES[p]).join(" / ");
    this.noticeTime = 2.5;
    if (kind === "dash" && this.dashCasts === 1) {
      this.notice = "JUMP + AIR DASH OVER THE SWEEP";
      this.noticeTime = 4;
    }
  }
  attack(kind: Attack) {
    if (kind === "scythe") {
      if (!this.pattern.length) this.prepareScythe();
      this.waveClock = 0;
      this.waveQueue = this.pattern.map((part, i) => [
        i * (part === "dash" ? 2 : 1.15),
        part,
      ]);
      this.launchWave(this.waveQueue.shift()![1]);
    } else {
      this.volleyTarget = this.center;
      this.fireVolley(kind);
      this.burstQueue.push([this.clock + 0.24, kind]);
    }
  }
  fireVolley(kind: Attack) {
    const role = kind === "raven" ? "raven" : "eye";
    if (this.nodes[role] <= 0) return;
    this.sound(role === "raven" ? "raven" : "skull");
    const [sx, sy] = this.nodeCenter(role),
      [px, py] = this.volleyTarget ?? this.center;
    const count = Math.min(
        5,
        role === "raven" ? 3 + this.phase : 1 + 2 * this.phase,
      ),
      speed = (role === "raven" ? 225 : 285) + this.phase * 15;
    this.nodeFire[role] = 0.2;
    this.burst(sx, sy, 0xff3322, 12);
    for (let i = 0; i < count; i++) {
      const a = Math.atan2(py - sy, px - sx) + (i - (count - 1) / 2) * 0.27;
      this.spawn(
        sx,
        sy,
        Math.cos(a) * speed,
        Math.sin(a) * speed,
        true,
        role === "raven" ? "raven" : "skull",
        7,
      );
    }
  }
  step(dt: number, input: Controls = {}) {
    dt = clamp(dt, 0, 0.04);
    this.previousX = this.x;
    this.previousY = this.y;
    this.clock += dt;
    this.swingTime = Math.max(0, this.swingTime - dt);
    this.landingAge = Math.max(0, this.landingAge - dt);
    this.brakeAge = Math.max(0, this.brakeAge - dt);
    let n = 0;
    for (const p of this.particles) {
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.vy += (p.dust ? -8 : 120) * dt;
      p.life -= dt;
      if (p.life > 0) this.particles[n++] = p;
      else this.particlePool.push(p);
    }
    this.particles.length = n;
    let recovering = this.hitAge !== null;
    if (this.hitAge !== null) {
      this.hitAge += dt;
      if (this.hitAge >= 0.55) {
        this.hitAge = null;
        if (this.hp > 0) {
          this.x = this.respawnAnchor[0];
          this.y = FLOOR;
          this.vy = this.jumpsUsed = this.slideCooldown = this.slideBuffer = 0;
          this.dashUsed = this.wasJump = this.wasSlide = this.duck = false;
          this.invuln = 3;
          this.sound("respawn");
          this.previousX = this.x;
          this.previousY = this.y;
        }
      }
    }
    let {
      move = 0,
      jump = false,
      duck = false,
      shoot = false,
      aim = null,
      aimUp = false,
      slide = false,
      slidePressed = false,
    } = input;
    if (recovering) {
      move = 0;
      jump = duck = shoot = aimUp = slide = slidePressed = false;
      aim = null;
    }
    this.shootHeld = shoot;
    if (this.state === "dying") {
      this.deathAge += dt;
      this.deathBlastTimer -= dt;
      if (
        0.45 < this.deathAge &&
        this.deathAge < 2.7 &&
        this.deathBlastTimer <= 0
      ) {
        this.sound("death_blast", 0.22);
        this.deathBlastTimer = 0.16;
        this.burst(
          W * 0.57 + this.deathOffset[0] + (80 + Math.random() * 250) * 0.96,
          FLOOR + this.deathOffset[1] - (80 + Math.random() * 360) * 0.96,
          0xffaa33,
          32,
        );
      }
      this.slideTime = this.dashTime = 0;
      this.moving = this.duck = false;
      this.vy += 1250 * dt;
      this.y = Math.min(FLOOR, this.y + this.vy * dt);
      if (this.y === FLOOR) this.vy = 0;
      if (this.deathAge >= 4.2) {
        this.sound("defeat");
        this.state = "won";
        this.notice = "MERGE IT";
        this.noticeTime = 999;
      }
      return;
    }
    if (this.state !== "play") return;
    const wasRunning = this.wasRunning,
      wasGrounded = this.y >= FLOOR - 0.2;
    for (const [role, kind] of [
      ["eye", "aimed"],
      ["raven", "raven"],
    ] as const)
      if (
        this.nodes[role] > 0 &&
        this.warning !== kind &&
        !this.burstQueue.some((q) => q[1] === kind)
      )
        this.patrol[role] += dt;
    if (this.warning !== "scythe" && this.swingTime <= 0) this.bossMotion += dt;
    this.noticeTime = Math.max(0, this.noticeTime - dt);
    this.invuln = Math.max(0, this.invuln - dt);
    this.fire -= dt;
    for (const key of [
      "muzzle",
      "bossFlash",
      "jumpFlash",
      "slideTime",
      "slideCooldown",
      "dashTime",
      "slideBuffer",
    ] as const)
      this[key] = Math.max(0, this[key] - dt);
    for (const role of ["eye", "raven"] as const) {
      this.nodeFire[role] = Math.max(0, this.nodeFire[role] - dt);
      this.nodeFlash[role] = Math.max(0, this.nodeFlash[role] - dt);
    }
    let grounded = this.y >= FLOOR - 0.1;
    if (grounded) {
      this.jumpsUsed = 0;
      this.dashUsed = false;
      this.dashTime = 0;
    } else if (!this.jumpsUsed) this.jumpsUsed = 1;
    if (slidePressed || (slide && !this.wasSlide)) {
      if (!grounded && !this.dashUsed) {
        this.sound("dash");
        this.dashUsed = true;
        this.dashTime = 0.18;
        this.slideBuffer = 0;
        this.dashDirection = move ? Math.sign(move) : this.facing;
        this.burst(this.x, this.y - 35, 0xd9d1a6, 10);
      } else if (grounded) this.slideBuffer = 0.18;
    }
    if (this.slideBuffer > 0 && grounded && this.slideCooldown <= 0) {
      this.sound("slide");
      this.slideTime = 0.42;
      this.slideCooldown = 0.65;
      this.slideBuffer = 0;
      this.slideDirection = move ? Math.sign(move) : this.facing;
    }
    this.wasSlide = slide;
    if (jump && !this.wasJump && this.jumpsUsed < 2) {
      this.sound(this.jumpsUsed === 1 ? "double_jump" : "jump");
      this.jumpsUsed++;
      this.vy = this.jumpsUsed === 1 ? -510 : -475;
      this.slideTime = this.dashTime = this.slideBuffer = 0;
      grounded = false;
      if (this.jumpsUsed === 2) {
        this.jumpFlash = 0.24;
        this.burst(this.x, this.y, 0xd9d1a6, 12);
      }
    }
    this.wasJump = jump;
    this.duck = (duck || this.sliding) && grounded;
    if (move) this.facing = Math.sign(move);
    const wasAirborne = this.y < FLOOR - 0.1;
    if (this.dashTime <= 0) {
      this.vy += 1250 * dt;
      this.y += this.vy * dt;
    }
    if (wasAirborne && this.y >= FLOOR) this.sound("land", 0.15);
    if (this.y >= FLOOR) {
      this.y = FLOOR;
      this.vy = this.jumpsUsed = 0;
      this.dashUsed = false;
    }
    const oldX = this.x;
    let speed = this.sliding
      ? this.slideDirection * (280 + (240 * this.slideTime) / 0.42)
      : move * (this.duck ? 110 : 240);
    if (this.dashTime > 0) {
      speed = this.dashDirection * 620;
      this.particle(
        this.x - this.dashDirection * 12,
        this.y - 32,
        -this.dashDirection * 80,
        0,
        0.16,
        0xd9d1a6,
        5,
      );
    }
    this.x = clamp(this.x + speed * dt, 22, W - 22);
    this.moving = Math.abs(this.x - oldX) > 0.001 && !this.duck;
    if (!recovering && this.y >= FLOOR - 0.1)
      this.respawnAnchor = [this.x, this.y];
    if (this.moving && !this.sliding && this.y >= FLOOR - 0.2) {
      if (!wasRunning) this.runPhase = 0;
      this.runPhase += Math.abs(this.x - oldX) / 24;
    }
    const running =
      this.y >= FLOOR - 0.2 &&
      this.hitAge === null &&
      this.moving &&
      !this.duck &&
      !this.sliding;
    const direction = Math.sign(this.x - oldX) || this.runDirection,
      landing = this.y >= FLOOR - 0.2 && !wasGrounded;
    if (landing) this.landingAge = 0.18;
    if (running && wasRunning && direction !== this.runDirection)
      this.brakeAge = 0.1;
    this.dustTimer -= dt;
    if (
      (running && (!wasRunning || direction !== this.runDirection)) ||
      landing ||
      (this.sliding && this.dustTimer <= 0)
    ) {
      this.dustTimer = 0.035;
      for (let i = 0; i < (landing ? 4 : this.sliding ? 3 : 6); i++) {
        const side = landing ? (i % 2 ? 1 : -1) : direction;
        this.particle(
          this.x - side * (11 + (i % 3) * 4),
          this.y - 2,
          -side * (35 + i * 13),
          -12 - (i % 3) * 8,
          0.32 + (i % 3) * 0.055,
          0xffffff,
          10 + (i % 3) * 3,
          true,
        );
      }
    }
    this.runDirection = direction;
    this.wasRunning = running;
    this.aim =
      shoot && aim
        ? aim
        : aimUp
          ? [this.x + this.facing * 100, this.center[1] - 102]
          : null;
    if (this.aim) this.facing = this.aim[0] >= this.x ? 1 : -1;
    const [wx, wy, angle] = this.weaponPose(),
      px = wx + Math.cos(angle) * 45.85,
      py = wy + Math.sin(angle) * 45.85;
    if (!this.shielded) {
      this.exposed -= dt;
      if (this.exposed <= 0) {
        this.sound("reform");
        this.nodeMax = 12 + this.phase * 2;
        this.nodes = { eye: this.nodeMax, raven: this.nodeMax };
        this.notice = "WEAK POINTS REFORMED";
        this.noticeTime = 2;
      }
    }
    if (shoot && this.fire <= 0) {
      this.shotsFired++;
      this.fire = 0.1 + Math.max(this.fire, -dt);
      this.muzzle = 0.06;
      this.spawn(px, py, Math.cos(angle) * 800, Math.sin(angle) * 800);
    }
    this.burstQueue = this.burstQueue.filter(([due, kind]) => {
      if (due > this.clock) return true;
      this.fireVolley(kind);
      return false;
    });
    this.waveClock += dt;
    while (this.waveQueue.length && this.waveQueue[0][0] <= this.waveClock)
      this.launchWave(this.waveQueue.shift()![1]);
    const wavesActive =
      this.waveQueue.length > 0 ||
      this.shots.some((b) => b.kind.startsWith("scythe_"));
    if (!wavesActive && !this.burstQueue.length) this.attackTimer -= dt;
    if (this.warning) {
      this.warningTime -= dt;
      if (this.warningTime <= 0) {
        this.attack(this.warning);
        this.warning = null;
        this.attackTimer = 1.65 - this.phase * 0.15;
      }
    } else if (
      this.attackTimer <= 0 &&
      !wavesActive &&
      !this.burstQueue.length
    ) {
      const sequence: Attack[] = ["aimed", "raven", "aimed", "scythe", "raven"];
      let next = sequence[this.attackNumber % 5];
      while (
        next !== "scythe" &&
        this.nodes[next === "raven" ? "raven" : "eye"] <= 0
      )
        next = sequence[++this.attackNumber % 5];
      const active = this.shots.filter((b) => b.enemy && b.life > 0).length;
      if (active > (next === "scythe" ? 0 : 4)) this.attackTimer = 0.08;
      else {
        this.warning = next;
        this.attackNumber++;
        if (next === "scythe") this.sound("charge");
      }
      this.warningTime = this.warning === "scythe" ? 1.5 : 0.95;
      if (this.warning === "scythe") {
        this.prepareScythe();
        if (
          this.pattern.length === 1 &&
          this.pattern[0] === "dash" &&
          !this.dashCasts
        )
          this.warningTime = 2.1;
      }
    }
    for (const b of this.shots) {
      if (b.life <= 0) continue;
      const ox = b.x,
        oy = b.y;
      b.px = ox;
      b.py = oy;
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      b.life -= dt;
      if (b.enemy) {
        if (b.kind.startsWith("scythe_")) {
          const kind = b.kind.slice(7) as Wave,
            [top, bottom] = band(kind),
            height = this.sliding ? 46 : this.duck ? 62 : 80,
            half = kind === "dash" ? 150 : 30;
          if (
            Math.min(ox, b.x) - half < this.x + 14 &&
            Math.max(ox, b.x) + half > this.x - 14 &&
            this.y > top &&
            this.y - height < bottom
          )
            this.hurt();
        } else {
          const [rx, ry] =
              b.kind === "skull"
                ? [16, 16]
                : b.kind === "raven"
                  ? [19, 14]
                  : [3, 3],
            [l, t, r, bot] = this.hitbox;
          if (
            segmentBox(ox, oy, b.x, b.y, [l - rx, t - ry, r + rx, bot + ry])
          ) {
            this.hurt();
            b.life = 0;
          }
        }
      } else if (this.hitTarget(ox, oy, b.x, b.y, b.damage)) b.life = 0;
    }
    n = 0;
    for (const b of this.shots) {
      if (
        b.life > 0 &&
        (b.kind === "scythe_dash" ? -180 : -30) < b.x &&
        b.x < W + 180 &&
        -30 < b.y &&
        b.y < H + 30 &&
        n < 350
      )
        this.shots[n++] = b;
      else this.shotPool.push(b);
    }
    this.shots.length = n;
  }
}
