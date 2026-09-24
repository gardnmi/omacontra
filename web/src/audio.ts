import type { Manifest } from "./renderer";
const PRIORITY: Record<string, number> = {
  rupture: 4,
  defeat: 4,
  player_death: 4,
  hurt: 3,
  raven_break: 3,
  eye_break: 3,
  expose: 2,
  reform: 2,
  sweep: 2,
  skull: 2,
  raven: 2,
  charge: 2,
};
const priority = (name: string) => PRIORITY[name] ?? 1;
/** Stream music, decode short samples once, cap voices and replace impact tails. */
export class GameAudio {
  private context: AudioContext | null = null;
  private gain: GainNode | null = null;
  private buffers = new Map<string, AudioBuffer>();
  private voices = new Map<string, AudioBufferSourceNode>();
  private takes = new Map<string, number>();
  readonly music = new Audio();
  muted = false;
  ready = false;
  async init(manifest: Manifest) {
    // Called directly by the start click/keypress, not before browser activation.
    this.context ??= new AudioContext();
    await this.context.resume();
    if (!this.gain) {
      this.gain = this.context.createGain();
      const limiter = this.context.createWaveShaper();
      const curve = new Float32Array(2048);
      for (let i = 0; i < curve.length; i++)
        curve[i] = Math.max(
          -0.1,
          Math.min(0.1, (i * 2) / (curve.length - 1) - 1),
        );
      limiter.curve = curve;
      this.gain.connect(limiter);
      limiter.connect(this.context.destination);
    }
    // Same +5 dB effect gain, 10% boost and -20 dB ceiling as the desktop mixer.
    this.gain.gain.value = this.muted ? 0 : 10 ** (5 / 20) * 1.1;
    if (this.ready) return;
    const names = Object.keys(manifest.audio);
    // Limit concurrent requests instead of decoding the full sound bank at once.
    let next = 0;
    await Promise.all(
      Array.from({ length: 4 }, async () => {
        while (next < names.length) {
          const name = names[next++],
            response = await fetch(`game/${manifest.audio[name]}`);
          if (!response.ok) throw new Error(`Sound download failed: ${name}`);
          this.buffers.set(
            name,
            await this.context!.decodeAudioData(await response.arrayBuffer()),
          );
        }
      }),
    );
    this.music.src = `game/${manifest.music}`;
    this.music.preload = "metadata";
    this.music.loop = true;
    this.music.volume = 0.7;
    this.music.muted = this.muted;
    this.ready = true;
  }
  play(events: string[]) {
    for (const name of events) {
      if (!this.context || !this.gain || this.muted) continue;
      const take = (this.takes.get(name) ?? 0) % 3;
      this.takes.set(name, take + 1);
      const buffer =
        this.buffers.get(take ? `variants/${name}-${take}` : name) ??
        this.buffers.get(name);
      if (!buffer) continue;
      this.voices.get(name)?.stop();
      this.voices.delete(name);
      if (this.voices.size >= 6) {
        const quietest = [...this.voices.keys()].reduce((a, b) =>
          priority(a) <= priority(b) ? a : b,
        );
        if (priority(quietest) > priority(name)) continue;
        this.voices.get(quietest)?.stop();
        this.voices.delete(quietest);
      }
      const source = this.context.createBufferSource();
      source.buffer = buffer;
      source.connect(this.gain);
      this.voices.set(name, source);
      source.onended = () => {
        if (this.voices.get(name) === source) this.voices.delete(name);
        source.disconnect();
      };
      source.start();
    }
    events.length = 0;
  }
  async resume() {
    if (this.context) await this.context.resume();
    if (this.ready) await this.music.play().catch(() => {});
  }
  pause() {
    this.music.pause();
    void this.context?.suspend();
  }
  clear() {
    for (const voice of this.voices.values()) voice.stop();
    this.voices.clear();
  }
  setMuted(value: boolean) {
    this.muted = value;
    this.music.muted = value;
    if (this.gain && this.context)
      this.gain.gain.setTargetAtTime(
        value ? 0 : 10 ** (5 / 20) * 1.1,
        this.context.currentTime,
        0.02,
      );
  }
}
