# Full browser port

Branch: `feature/web-port`. Browser entry point: `web/index.html`.
See [build/play instructions](../web/README.md).

## Runtime boundary

The complete native campaign is packaged byte-for-byte into `campaign/game.zip`.
Pyodide 314.0.7 runs it in a module worker, with the original variable timestep
capped at 40 ms. Boss rules, collisions, seeds, animations, cinematic timings,
menus, life awards, continue behavior, and score categories have one source of
truth: `src/omacontra/`.

`web/runtime/browser_host.py` substitutes only platform interfaces:

- A host around the existing `BossApp` replaces GTK and compositor calls.
- Native sprite alpha/matte processing and pixel-derived cloud/atmosphere stamps
  happen during asset export, using the actual native preparation functions.
- `runtime/cairo.py` records drawing operations. `src/campaign/canvas.ts` executes
  them on worker-owned OffscreenCanvas surfaces. Cached native surfaces remain
  cached; one completed ImageBitmap crosses to the page per frame.
- Sprite crops/flips and reflected water strips use equivalent direct image
  draws, avoiding hundreds of transient patterns/transform commands per frame.
- Original short audio recordings go through a bounded Web Audio mixer with the
  native gain and soft volume ceiling. Music uses streaming media channels,
  retaining the opening/shuffle/finale/jukebox rules and continuous shield sound.
- The native JSON profile is mirrored to browser localStorage. No desktop files
  or system commands are available to the game.

The original three `.ttframes` clips are loaded and decompressed by the original
screensaver player. Only its BGRA-to-browser pixel upload is adapted. The worker
keeps the native four-frame cache; terminal effects are not recreated in a new
visual style.

Input arrives as ordered key/pointer events. Very short gameplay presses stay
held for one simulation tick before release so browser event batching cannot
swallow a jump or shot. Menu/secret-code presses stay immediate. Focus changes
use the original pause/reset behavior. Rendering never scales with device DPI.

## Coverage

- All five encounters and their original subphases, weapons, transitions, and
  environmental effects.
- Opening and wine-cellar journey; highway/harbor transitions; mist arrival;
  both guardian rage closeups; dragon disarm and Tobi rescue; elevator/boarding;
  tethered space encounter; homecoming/ending.
- Native Start/mode, pause, controls, options, soundtrack, credits, results,
  boss-select, confirmation, and continue screens.
- Shuffled gameplay music, opening exclusion, fixed finale song starting at
  boarding and continuing on results; original stage effects and impact sounds.
- Unlimited secret, damage/life tracking, hardcore, life carry-over, ribbons,
  clear-time categories and persisted personal bests/settings.

The browser has an initial click-to-enable-audio gate and a page fullscreen
button. Quit returns to this gate because a webpage cannot close an arbitrary
browser tab. Records are browser-local, separate from the desktop installation.
Keyboard and mouse remain required. OS-specific window management is replaced
by normal browser/fullscreen behavior.

## Validation

`tools/check_campaign.py` verifies all packaged native modules against their
source bytes, all sound recordings against their originals, the screensaver
data, image hashes, and runtime notices. It fails on a stale Python archive.

Playwright exercises the complete browser adapter in Chromium and Firefox,
including progression into results, input, menus, sound selection, continue and
hardcore paths, persistence failures, and high DPI. The cinematic/art test also
renders transformation, finisher, rage, rescue, boarding, and ending boundaries.
Development setup hooks are gated by `import.meta.env.DEV`.

`tools/check_render_parity.py` compares twelve seeded render states against
native Cairo captures, allowing mean channel error below 4/255 in Chromium and 6/255 in Firefox
for differences in text/edge rasterization. Initial Chromium comparisons ranged
approximately 0.6–2.6/255 by channel; Firefox ranged approximately 0.9–5.0/255. This complements visual inspection; it does not prove
pixel identity at every animation frame.

Initial local headless Chromium samples measured roughly 6–15 ms of combined
worker simulation/drawing for typical gameplay; the harbor water dropped from
about 29 ms to 11 ms after the strip optimization. A later combat stress pass
included 175 active finale projectiles and the screensaver at roughly 11 ms at
the sampled 90th percentile. Highway samples occasionally exceeded the 16.7 ms
60 Hz budget. These are development-machine measurements, not low-end GPU
certification or whole-browser presentation latency. Test the actual browser
and hardware before publishing broad performance claims.

The desktop source/installer remains untouched. Publishing this branch or
merging it into the desktop release is a separate action.

## Build and notices

Generated browser artwork/audio/runtime files are ignored build output. Export
reads only `release-assets.txt`; it does not ship generation intermediates.
Hashed PNGs deduplicate identical source/prepared images. Music streams rather
than loading the complete soundtrack into decoded PCM memory.

Pyodide's JS/WASM and CPython standard library are copied unmodified from the
pinned npm package, with licenses and corresponding source links under
`web/licenses/`. Original game/asset notices are also included in the build.

Documentation consulted:

- https://pyodide.org/en/stable/usage/webworker.html
- https://pyodide.org/en/stable/usage/api/js-api.html
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas
- https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices
