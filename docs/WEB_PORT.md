# Browser port plan

Branch: `feature/web-port`, starting from v1.0.2.
Status: first Reaper browser playtest implemented in `web/`. See
[local playtest instructions](../web/README.md). The remaining campaign is not
yet ported. Chromium/Firefox checks and desktop simulation traces cover this
first milestone; low-end hardware performance still needs playtesting.

## Proposed approach

Build a TypeScript browser runtime with PixiJS GPU rendering, initially using
WebGL. Keep it in `web/`. Reuse existing artwork, sound recordings, encounter
constants, and animation geometry. Port simulation logic with the Python game
and its regression tests as the behavior reference. Avoid introducing a new
physics engine that would change jumps, slides, aiming, or collision rules.

The current desktop host uses GTK/GLib and Hyprland IPC (`boss_app.py`), Cairo
rendering (`rendering/frame_buffer.py` and stage renderers), SDL audio via ctypes
(`audio/weapon_audio.py`), and mpv processes (`audio/intro_music.py`). These need
browser implementations. The encounters already expose step functions, which
provides a useful boundary between simulation and presentation. A Python/WASM
approach could preserve more simulation code, but would still need replacement
rendering/audio and should be benchmarked before adopting it.

## Performance constraints

- Default to a 1280 x 720 drawing buffer, CSS-scaled with letterboxing; do not
  multiply rendering resolution by devicePixelRatio on high-DPI screens.
- Target 60 Hz simulation with interpolated rendering. Bound catch-up work and
  pause/reset timing on tab blur. Check gameplay parity carefully: the desktop
  currently uses variable dt capped at 40 ms.
- Reuse sprites and pool frequently created bullets/particles. Keep readable
  enemy projectiles and all collision checks at full fidelity; reduce only
  cosmetic effects when performance drops.
- Pack suitable sprites into stage-specific atlases. Cache static layers and
  bake expensive glows/smoke into textures when practical. Avoid full-screen
  blur and per-frame reconstruction of complex vector graphics.
- Load the title and first encounter first; preload the next encounter and
  release textures from completed scenes. Measure decoded texture memory as
  well as download size. The local assets tree is approximately 196 MiB and
  includes development material: do not copy it wholesale into the web build.
- Stream music with a media element; decode short effects into Web Audio buffers
  and limit simultaneous voices. Enable audio after a user gesture. Preserve the
  opening/gameplay/finale playlist rules and current muted player-gun behavior.
- Preserve Beams, Rings, Blackhole order in the finale. Benchmark browser-friendly
  playback of the precomputed animation before choosing a shader rewrite.
- Cache versioned assets with HTTP caching. Save profiles in browser storage,
  handle unavailable storage gracefully, and keep browser profiles separate
  from the desktop installation.

## First playable milestone

Port the Reaper encounter: actual DHH assets, running/weapon motion, jumping,
sliding, air dash, aiming, projectiles, damage, boss phases, and stage clear.
Include keyboard/mouse controls, focus reset, and a performance overlay. This
is the gate before porting the remaining four encounters and cinematics.

Validation should compare recorded input sequences against the desktop game,
including collision outcomes, shot cadence, cooldowns, and encounter transitions.
Do not expect Python and JavaScript random generators to match automatically;
use explicit seeded test fixtures. Measure frame-time percentiles, long stalls,
texture memory estimates, startup download size, and stage-transition loading
on Chromium and Firefox, especially an integrated-GPU machine. A 60 fps target
means approximately 16.7 ms per frame; smoothness is not proven by average FPS.
The dragon effects and final bullet patterns need separate stress checks.

## Documentation consulted

- https://pixijs.com/8.x/guides/concepts/performance-tips
- https://pixijs.com/8.x/guides/components/assets
- https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices
