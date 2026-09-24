# Omacontra — full browser campaign

The complete five-stage game runs in the browser on `feature/web-port`:
Reaper, Quattro Run (including its robot phase), Tidebreaker and both guardians,
the Mist Gate dragon, and Black Moon. This includes the original opening,
inter-stage cinematics, Tobi's rescue, spaceship boarding, ending, menus,
continue screen, hardcore mode, secret code, soundtrack player, and results.

## Play locally

Requires Node.js 22.12+ and npm to build. Asset preparation also needs system
Python 3 and Pycairo, as used by the desktop game.

```sh
cd web
npm ci
npm run assets
npm run dev
```

Open **http://127.0.0.1:5173** and click **PLAY** to enable browser audio.
The original intro and Start screen follow. Players only need a browser; they
do not install Python, GTK, Hyprland, or the game itself.

Keyboard/mouse controls match the desktop game:

- A/D or left/right: move. W/up: aim upward; S/down: duck.
- Space/K: jump, then press again for a double jump.
- Shift: ground slide or air dash.
- Mouse + left button: aim/fire; J/Z: keyboard fire.
- E: interact in the harbor. Space also operates the car's jump.
- P/Escape: pause/menu. Enter: confirm and advance/skip eligible scenes.
- Space-stage movement uses both axes. Its existing thruster/dash rules apply.

The built-in Controls menu explains stage-specific actions. Fullscreen is below
the canvas. Switching tabs/windows pauses the game and clears held input.

Settings and records save locally in this browser under
`omacontra.campaign.profile.v1`. Standard, hardcore, and unlimited records remain
separate; boss-select practice runs cannot replace campaign records. Storage
errors are handled without preventing play.

## Build for a static host

```sh
npm run assets
npm run build
npm run preview
```

The production playtest is **http://127.0.0.1:4173**. Deploy the contents of
`dist/` on any static HTTP(S) host. Subdirectory hosting works with the relative
build paths. Opening `index.html` directly using `file://` is unsupported.

All runtime files are self-hosted, including the pinned Python/WebAssembly
runtime. There is no CDN, account, game server, or Python server dependency.
Images load as scenes need them, short effects are cached, and music streams.
Keep `campaign/credits/` and its runtime license/source notices with the build.
Use versioned deployment directories before enabling long-lived asset caching;
`index.html`, `game.zip`, and the asset manifest must belong to the same build.
This branch does not publish or alter the desktop installer/release.

## Cloudflare Pages hosting

Public game: **https://omacontra.pages.dev/**

The `omacontra` Pages project serves only static files. It has no Pages
Functions, server Worker, database, or R2 dependency. Under current Pages
pricing, static requests are free and unlimited. Keep future deployments
static-only to retain this hosting model.

To publish an update from the repository root, after testing:

```sh
npm --prefix web run assets
npm --prefix web run build
npx --yes wrangler@4.138.0 pages deploy web/dist --project-name omacontra --branch main
```

Wrangler must be signed into the owning Cloudflare account (`wrangler login`).
The `main` argument selects the Pages production environment; it does not merge
or change the checked-out Git branch. Direct Upload publishes the local build;
Git pushes do not automatically deploy it. Upload only `web/dist`, never the
repository or credential files. For a non-production preview, use another
`--branch` value. Keep Wrangler's local `.wrangler/` cache out of Git.

## Fidelity and performance

The browser executes the **same Python encounter, cinematic, and UI source** as
the desktop game, in a dedicated worker. A small platform adapter replaces GTK,
Cairo's output surface, desktop audio processes, and profile storage. This avoids
maintaining a second copy of every boss's rules. The renderer preserves the
original artwork, sprite crops, masks, lighting, particles, and animations.
Canvas and Cairo can differ slightly in edge/font rasterization.

Rendering stays at **1280 × 720**, including on high-DPI displays. Static layers
stay cached; moving-water strips and sprite draws have compact browser commands.
The original Beams → Rings → Blackhole frame data plays in the original order.
No attack patterns, hitboxes, or effects are removed to obtain the port.

Current desktop Chromium and Firefox are tested. Touch controls and controllers
are not implemented. Low-end hardware still needs hands-on playtesting; local
headless measurements are not a guarantee of 60 FPS on every device. See
[architecture and validation](../docs/WEB_PORT.md).

## Checks

```sh
npm run test:assets
npm test
npm run assets:prototype  # prepare the retained Reaper reference prototype
npx playwright install chromium firefox
npm run test:browser
npm run test:parity
```

The browser tests cover real keyboard/mouse handling, short taps, focus changes,
secret entry, progression, life carry-over, standard/hardcore continues, music,
records, settings, blocked storage, high DPI, loading errors, and original
cinematic/renderer states in both browsers. Native/browser image comparisons
cover twelve representative combat states. Captures/reports stay under ignored
`test-results/`. Run `python tools/test.py` from the repository root for the
native regression suite.

After Python-only changes, `npm run assets:code` rebuilds the source archive
quickly; use the full `assets` command after changing any image or asset list.
The development-only `window.__campaign` harness provides stage/scene setup and
frame measurements for tests. It is removed from the production JavaScript.

The earlier TypeScript/PixiJS Reaper prototype is retained at `/reaper.html` on
the dev server as a regression reference. It is not the production entry point.
