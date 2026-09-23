# Authentic Omarchy screensaver animations

Generated from installed ttfx 0.3.2, https://github.com/omacom-io/ttfx,
MIT-licensed Rust port of ChrisBuilds/terminaltexteffects (also MIT).
The included logo is the installed Omarchy screensaver branding.

Rebuild: `python tools/build_screensaver.py`.
The exporter invokes ttfx's deterministic length-prefixed frame output,
using a 96 x 30 centered canvas and seed 42. Effects run at Omarchy's
120 FPS timing and are sampled to 30 FPS for background playback.
Animation paths, glyphs and colors come directly from ttfx; the game
only dims their brightness to keep enemy projectiles readable.

Included: beams, rings, blackhole, fireworks, swarm, expand,
and colorshift. They cycle through the fight and reshuffle on repeat.
No ttfx process, terminal window or Python TTE package is needed at runtime.

## Runtime performance

The exporter also bakes frames into `.ttframes` files: indexed zlib-compressed
576 x 300 Cairo RGB24 pixels. Runtime keeps four decoded frames cached and
paints with nearest-neighbor scaling. It does not parse ANSI, build color
groups, allocate a full-screen glyph canvas, or draw terminal fonts.
The original `.json.gz` exports remain the rebuild inputs; run the exporter
with `--raster-only` to rebuild pixel frames without invoking ttfx.
Earth stops rendering when the transition reaches full opacity.
