type Music = {
  id: number;
  tracks: string[];
  active: boolean;
  paused: boolean;
  volume: number;
  effect: boolean;
  loop: boolean;
  generation: number;
};
type Channel = {
  element: HTMLAudioElement;
  gain: GainNode;
  state: Music;
  index: number;
};
type Voice = {
  source: AudioBufferSourceNode;
  gain: GainNode;
  priority: number;
  name: string;
  scope: string;
};
/** Original recordings and native sound events; bounded effects leave room for music. */
export class CampaignAudio {
  private context?: AudioContext;
  private master?: GainNode;
  private limiter?: WaveShaperNode;
  private buffers = new Map<string, Promise<AudioBuffer>>();
  private channels = new Map<number, Channel>();
  private voices: Voice[] = [];
  private epochs = new Map<string, number>();
  private contact?: Voice;
  private contactEpoch = 0;
  private hidden = false;
  private pendingMusic: Music[] = [];
  private files: string[] = [];
  constructor(private root: string) {
    void fetch(root + "manifest.json")
      .then((r) => r.json())
      .then((m) => {
        this.files = Object.keys(m.audio);
      })
      .catch(() => {});
  }
  async unlock() {
    if (!this.context) {
      this.context = new AudioContext();
      this.master = this.context.createGain();
      this.master.connect(this.context.destination);
      this.limiter = this.context.createWaveShaper();
      const curve = new Float32Array(65537);
      for (let i = 0; i < curve.length; i++)
        curve[i] = Math.max(
          -0.1,
          Math.min(0.1, (i / (curve.length - 1)) * 2 - 1),
        );
      this.limiter.curve = curve;
      this.limiter.connect(this.master);
    }
    const resumed = this.context.resume();
    // Flush boot state synchronously, before gameplay can emit newer state.
    for (const state of this.pendingMusic) this.music(state);
    this.pendingMusic = [];
    await resumed;
    this.preload(1);
  }
  visibility(hidden: boolean) {
    this.hidden = hidden;
    for (const c of this.channels.values()) this.play(c);
    if (hidden) this.clearAll();
  }
  private buffer(path: string) {
    let promise = this.buffers.get(path);
    if (!promise) {
      promise = fetch(this.root + path)
        .then((r) => {
          if (!r.ok) throw new Error(`Missing sound ${path}`);
          return r.arrayBuffer();
        })
        .then((b) => this.context!.decodeAudioData(b));
      this.buffers.set(path, promise);
    }
    return promise;
  }
  preload(level: number) {
    if (!this.context) return;
    const bank = ["", "reaper", "chase", "tide", "wyrm", "finale"][level];
    for (const file of this.files)
      if (
        file.endsWith(".wav") &&
        (file.startsWith(`audio/${bank}/`) ||
          file.startsWith("audio/menu/") ||
          file.startsWith("audio/continue/"))
      )
        void this.buffer(file).catch(() => {});
  }
  process(effects: any[], music: Music[]) {
    for (const state of music) this.music(state);
    if (!this.context) return;
    for (const e of effects) {
      if (e.kind === "effect") void this.effect(e);
      else if (e.kind === "clear") this.clear(e.scope);
      else if (e.kind === "contact") void this.shield(e.enabled, e.gain);
      else if (e.kind === "volume" && this.contact)
        this.contact.gain.gain.setTargetAtTime(
          e.gain,
          this.context.currentTime,
          0.015,
        );
    }
  }
  private music(state: Music) {
    if (!this.context) {
      this.pendingMusic = this.pendingMusic.filter((s) => s.id !== state.id);
      this.pendingMusic.push(state);
      return;
    }
    let c = this.channels.get(state.id);
    if (!c) {
      if (!state.active) return;
      const element = new Audio();
      element.preload = "auto";
      const gain = this.context.createGain();
      this.context.createMediaElementSource(element).connect(gain);
      gain.connect(this.master!);
      c = { element, gain, state, index: 0 };
      this.channels.set(state.id, c);
      element.addEventListener("ended", () => {
        const ch = this.channels.get(state.id)!;
        if (
          ch.state.active &&
          (ch.index + 1 < ch.state.tracks.length || ch.state.loop)
        ) {
          ch.index = (ch.index + 1) % ch.state.tracks.length;
          ch.element.src = this.root + ch.state.tracks[ch.index];
          this.play(ch);
        }
      });
      element.src = this.root + state.tracks[0];
    }
    const changed =
      (!c.state.active && state.active) ||
      c.state.generation !== state.generation ||
      c.state.tracks.join("|") !== state.tracks.join("|");
    c.state = state;
    // Music recordings are mastered much louder than the bounded effects mix.
    // Apply the browser mix trim at the output, including saved volume settings.
    // Start/unlock cues share this player but must keep their effects volume.
    const outputGain = state.volume * (state.effect ? 1 : 0.25);
    if (this.context.state === "running")
      c.gain.gain.setTargetAtTime(outputGain, this.context.currentTime, 0.025);
    else c.gain.gain.value = outputGain;
    if (changed) {
      c.element.pause();
      c.index = 0;
      if (state.active) c.element.src = this.root + state.tracks[0];
      else c.element.removeAttribute("src");
    }
    this.play(c);
  }
  private play(c: Channel) {
    if (c.state.active && !c.state.paused && !this.hidden)
      void c.element.play().catch(() => {});
    else c.element.pause();
  }
  private stop(v: Voice) {
    try {
      v.source.stop();
    } catch {}
    v.source.disconnect();
    v.gain.disconnect();
    this.voices = this.voices.filter((x) => x !== v);
  }
  private clear(scope: string) {
    this.epochs.set(scope, (this.epochs.get(scope) ?? 0) + 1);
    for (const v of [...this.voices]) if (v.scope === scope) this.stop(v);
  }
  private clearAll() {
    for (const scope of new Set(this.voices.map((v) => v.scope)))
      this.clear(scope);
    void this.shield(false, 0);
  }
  private async effect(e: any) {
    if (this.hidden) return;
    const epoch = this.epochs.get(e.scope) ?? 0,
      started = performance.now();
    try {
      const buffer = await this.buffer(e.path);
      if (
        this.hidden ||
        (this.epochs.get(e.scope) ?? 0) !== epoch ||
        performance.now() - started > 250
      )
        return;
      for (const old of [...this.voices])
        if (old.scope === e.scope && old.name === e.name) this.stop(old);
      const bank = this.voices.filter((v) => v.scope === e.scope);
      if (bank.length >= 6) {
        const weakest = bank.reduce((a, b) =>
          a.priority <= b.priority ? a : b,
        );
        if (weakest.priority > e.priority) return;
        this.stop(weakest);
      }
      const source = this.context!.createBufferSource(),
        gain = this.context!.createGain();
      source.buffer = buffer;
      gain.gain.value = e.gain;
      source.connect(gain);
      gain.connect(this.limiter!);
      const voice = {
        source,
        gain,
        priority: e.priority,
        name: e.name,
        scope: e.scope,
      };
      this.voices.push(voice);
      source.onended = () => this.stop(voice);
      source.start();
    } catch (error) {
      console.warn(error);
    }
  }
  private async shield(enabled: boolean, gain: number) {
    const epoch = ++this.contactEpoch;
    if (!enabled) {
      if (this.contact) {
        const old = this.contact;
        this.contact = undefined;
        old.gain.gain.setTargetAtTime(0, this.context!.currentTime, 0.015);
        setTimeout(() => this.stop(old), 90);
      }
      return;
    }
    if (this.contact || !this.context || this.hidden) return;
    try {
      const buffer = await this.buffer("audio/finale/loops/shield.wav");
      if (epoch !== this.contactEpoch || this.hidden) return;
      const source = this.context.createBufferSource(),
        node = this.context.createGain();
      source.buffer = buffer;
      source.loop = true;
      node.gain.value = 0;
      node.gain.setTargetAtTime(gain, this.context.currentTime, 0.015);
      source.connect(node);
      node.connect(this.limiter!);
      this.contact = {
        source,
        gain: node,
        priority: 5,
        name: "shield",
        scope: "contact",
      };
      source.start();
    } catch (error) {
      console.warn(error);
    }
  }
  snapshot() {
    return [...this.channels.values()].map((c) => ({
      id: c.state.id,
      active: c.state.active,
      paused: c.element.paused,
      track: c.state.tracks[c.index],
      time: c.element.currentTime,
      gain: c.gain.gain.value,
    }));
  }
}
