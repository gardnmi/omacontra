# Omacontra browser playtest

A playable port of **the Reaper encounter**, on `feature/web-port`.
The native game and installer remain separate from this browser build.

## Play locally

From this directory, with Node.js 22.12+ (or a newer supported LTS) and npm:

```sh
npm ci
npm run assets
npm run dev
```

Open **http://127.0.0.1:5173**. Click **Enter the fight** to enable audio and start.
The asset preparation step uses system Python 3 and Pycairo, already required
by the desktop game. The finished browser build needs neither Python nor GTK.

- A/D or arrows: move; W/up: aim upward when using keyboard firing.
- Space/K: jump; release and press again for a double jump.
- Shift: slide on the ground; dash once while airborne.
- Mouse + left button: aim and fire; J/Z: fire with keyboard.
- S/down: duck. P/Escape: pause. R: open pause/restart.
- F3 or Performance: frame-time overlay. Fullscreen and sound controls sit below
  the game. Moving to another tab/window automatically pauses and clears input.
- Unlimited practice lives are optional. Hits are still counted, and practice
  clears never overwrite the standard personal best.

## Included

Original arena and Reaper artwork; authored DHH run/carry frames, separate aiming
rig, jump/slide/double-jump/air-dash rules; both turrets, exposure/reform, all scythe
patterns, damage/respawn, boss destruction and stage clear. Existing Reaper sound
samples and streamed Contra music. Standard clear times save in browser storage
under `omacontra.web.reaper.best`, separately from desktop records.

This first milestone does **not** yet include the full opening cinematic, the
other four stages, full campaign menus/continue screen, or the complete shuffled
soundtrack. Environmental effects are a lightweight browser implementation;
visual/audio parity still needs human playtesting. Keyboard/mouse desktop browsers
are the initial target; touch controls are not implemented.

## Production build

```sh
npm run assets
npm run build
npm run preview
```

Serve `dist/` over HTTP(S) on a static host. Relative asset URLs support subpaths.
Do not launch `dist/index.html` as a `file://` URL. No game server is required.
Use compression for JS/CSS/JSON, and version the deployment path before applying
long-lived caching to the generated `game/` assets. Keep the shipped credits.
Publishing is a separate step; this branch does not deploy or change the release.

## Checks

```sh
npm test
npx playwright install chromium firefox
npm run test:browser
```

Playwright may require its documented host libraries on Linux. Browser tests use
an isolated dev server, test-only access gated behind `import.meta.env.DEV`, and
record screenshots under ignored `test-results/`. The production build removes
that access. Tests cover combat, focus, controls, high DPI, failed loading,
practice mode, standard results and persistent records. Python reference traces
can be regenerated after intentional desktop-rule changes:

```sh
/usr/bin/python3 tools/export_fixtures.py
```

`tools/export_assets.py` reads original artwork through the desktop's alpha/chroma
handling, prepares the authored poses at 2x display size, and packs them into one
2048-square atlas. It does not generate new artwork. Build outputs are ignored;
source assets and source credits remain authoritative.

## Performance

- Fixed 1280 x 720 drawing buffer, independent of display/device pixel ratio.
- GPU sprite batching, reusable display objects, pooled bullets and particles.
- 60 Hz simulation with interpolated player/projectile rendering, bounded
  catch-up, and automatic pause when hidden.
- Roughly 9.4 MiB of encounter assets including streamed music; arena + atlas
  are about 3.4 MiB downloaded and 19.5 MiB of base decoded RGBA texture storage
  (excludes browser/GPU overhead and audio).
- Existing short effects decoded once; six simultaneous voices maximum. Music
  streams separately. The player machine gun stays silent as in the native game.
- Cosmetic particle counts automatically halve when the recent 95th percentile
  frame interval exceeds 24 ms; collision geometry and attacks stay unchanged.

The overlay's render time measures CPU submission, not total GPU execution.
Headless Chromium/Firefox smoke runs are useful checks, not proof of performance
on integrated graphics. Validate a normal browser on the intended low-end hardware
before claiming the 60 FPS target. Stress later dragon/finale stages separately.
