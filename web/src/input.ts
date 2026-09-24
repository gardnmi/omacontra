import type { Controls, Point } from "./fight";
export class Input {
  readonly keys = new Set<string>();
  readonly held = new Set<string>();
  mouse = false;
  aim: Point | null = null;
  slidePressed = false;
  clear() {
    this.keys.clear();
    this.held.clear();
    this.mouse = false;
    this.aim = null;
    this.slidePressed = false;
  }
  consume() {
    this.keys.clear();
    this.mouse = false;
    this.slidePressed = false;
  }
  down(code: string) {
    if (this.held.has(code)) return false;
    this.held.add(code);
    this.keys.add(code);
    if (code.startsWith("Shift")) this.slidePressed = true;
    return true;
  }
  up(code: string) {
    this.held.delete(code);
    this.keys.delete(code);
  }
  controls(): Controls {
    const has = (...codes: string[]) => codes.some((c) => this.keys.has(c));
    const result = {
      move:
        Number(has("KeyD", "ArrowRight")) - Number(has("KeyA", "ArrowLeft")),
      jump: has("Space", "KeyK"),
      duck: has("KeyS", "ArrowDown"),
      shoot: this.mouse || has("KeyJ", "KeyZ"),
      aim: this.mouse ? this.aim : null,
      aimUp: has("KeyW", "ArrowUp"),
      slide: has("ShiftLeft", "ShiftRight"),
      slidePressed: this.slidePressed,
    };
    this.slidePressed = false;
    return result;
  }
}
