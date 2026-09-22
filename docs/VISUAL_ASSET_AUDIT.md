# Visual asset quality pass

Reviewed all 56 existing PNG sheets, the canonical character reference, the five
encounter renderers, and all ten cinematic sequences. The principal quality gaps
were procedural props and effects drawn on top of the detailed illustrations.
Four new atlases supply 24 illustrated sprite frames for those gaps.

## Changes made

| Area | Quality gap | Replacement in the game |
| --- | --- | --- |
| Foundry platforms | Plain black support bars beneath a thin strip of floor | Riveted steel decks, amber lamps, cross-braced supports and planted feet. Deck thickness stays fixed at every platform height. |
| Foundry armory | Rectangle cabinet and line-drawn weapon | Matched closed/open maintenance cabinet, padded weapon compartment, and copper-coil arc rifle. Rifle remains visible when firing stops. |
| Foundry fire jet | Straight parallel colored stripes | Three illustrated turbulent flame poses blended into a looping animation, with pilot flame and dissipating vapor. |
| Foundry floor attack | Row of short colored lines | Continuous animated molten fire strip with varied crests. |
| Foundry cannon / rescue discharge | Flat beam lines and wireframe cone | Continuous illustrated fire stream anchored to the existing discharge path. |
| Foundry barrages | Flat circles and straight light walls | Fractured molten cinders with small interleaved flames; each cinder stays anchored to its collidable bolt. |
| Warden exhaust | Overlapping translucent circles | Layered silver steam sprites rising from the vents. |
| Quattro ramp | Outlined triangle with a few struts | Riveted steel jump ramp, worn hazard strip and triangular girder. High lip remains on the left. |
| Highway barriers | Black rectangles with diagonal lines | Battered barricades with feet, inset panels and amber lamps. |
| Highway boost / rocket exhaust | Colored line segments | Animated hot exhaust attached to the existing nozzle positions. |
| Highway mortar impact | Expanding glow circle | Existing high-quality ground explosion animation, reused at the impact position. |
| Shared weapons | Flat polygon muzzle flashes | Directional illustrated combustion flash attached to the barrel. Used by DHH and the Tidebreaker guardians. |
| Movement / damage smoke | Brown rectangles, circles and radial blobs | Detailed smoke puffs for jump dust, skid dust and damaged machinery. |
| Tidebreaker guardian shots | Plain disks and an outlined pressure ring | Incandescent slugs, cyan energy pearls and a shaded turbulent pressure ring. |
| Orbital AI shots | Rectangles, diamonds, circles and straight needles | Cyan pearls, amber organic spores, violet crystalline shards and red plasma needles. Distinct silhouettes and colors remain visible in dense patterns. |

The detailed arenas, bosses, vehicles, waves, harpoon, space explosion and portal
remain the visual references. Canonical character routing remains in
`character_assets.py`. The recovered original opening and its animated wine cellar
were preserved. Health bars, aiming marks, thin tracers and tiny sparks remain
deliberately simple so the action is readable.

## Art sources

Generated with the built-in `image_gen.imagegen` tool, using existing game artwork
as style references. Full prompts, reference filenames and generated source paths
are in [quality-prompts.json](../assets/quality-prompts.json).

- [industrial-props-v1.png](../assets/industrial-props-v1.png): platform, closed/open cabinet, arc rifle, barricade, ramp.
- [combat-effects-v1.png](../assets/combat-effects-v1.png): three flame-jet poses, muzzle flash, smoke, steam.
- [hostile-projectiles-v1.png](../assets/hostile-projectiles-v1.png): six projectile materials and silhouettes.
- [furnace-streams-v1.png](../assets/furnace-streams-v1.png): three horizontal discharge poses and three floor-fire poses.

All four retain true alpha. Violet projectile pixels bypass the old magenta
transparency decoder. Fine projectile art is filtered once into small cached
stamps to avoid shimmering when reduced to gameplay size. Flame loops are blended
once into bounded cached surfaces, rather than allocating a new group each frame.
Shared atlas capacity is bounded at 16 sheets to accommodate the added effects.

This pass changes drawing only: attack timing, damage, movement, collision boxes,
boss health, story beats and audio settings are unchanged.

## Review artifacts

- [Before contact sheet](../review/quality-pass/before/contact-sheet.png)
- [After contact sheet](../review/quality-pass/after/contact-sheet.png)
- [Animated effects preview](../review/quality-pass/after/effects-motion.mp4)
- [Foundry before](../review/quality-pass/before/04-jet.png) / [Foundry after](../review/quality-pass/after/04-jet.png)
- [Guardian projectiles](../review/quality-pass/after/03-guardians.png)
- [Orbital projectile patterns](../review/quality-pass/after/05-orbit-3.png)
- [Render timings](../review/quality-pass/render-timings.json)

Generate 13 gameplay review states and an eight-second effects video:

```sh
python asset_review.py --output /tmp/omacontra-art --video
```

Review the actual scenes interactively:

```sh
python main.py --level 4
python main.py --level 5
python main.py --cutscene foundry-rescue
```

## Validation

- 127 tests pass, including scripted encounter completion, movement mechanics,
  finale phase progression, cinematic rendering and character transparency.
- All ten cutscenes rendered at six timeline positions, including zero and final
  frames. The main changes were also visually inspected at 1280 × 720.
- The motion preview renders 240 frames through jet buildup, firing, shutoff and
  the floor-fire animation.
- Timings measure warmed offscreen Cairo rendering at 1280 × 720. They do not
  measure compositor/display latency or replace human playtesting.

## Complete PNG inventory

Includes the four new atlases. Original character sheets used as alpha mattes are
kept deliberately; obsolete alternatives are identified below so they are not
accidentally reintroduced into active scenes. `assets/reference/canonical-characters.png`
is the separate identity reference for Tobi and DHH.

| File | Review result |
| --- | --- |
| `combat-effects-v1.png` | New detailed replacement atlas — integrated |
| `cover-v1.png` | Legacy source, not drawn in current game — retained for recovery |
| `dhh-body-canonical.png` | Active canonical character art — retained |
| `dhh-body.png` | Canonical replacement displayed |
| `dhh-portal-reach-canonical.png` | Active canonical character art — retained |
| `dhh-portal-reach.png` | Original retained as alpha matte; canonical art displayed |
| `dhh-space-rear.png` | Active detailed art — retained |
| `dhh-space-walk-canonical.png` | Active canonical character art — retained |
| `dhh-space-walk.png` | Original retained as alpha matte; canonical art displayed |
| `dhh-sprites.png` | Legacy source, not drawn in current game — retained for recovery |
| `dhh-weapon.png` | Active detailed art — retained |
| `finale-atlas.png` | Active detailed art — retained |
| `finale-car-rear-canonical.png` | Active canonical character art — retained |
| `finale-car-rear.png` | Original retained as alpha matte; canonical art displayed |
| `finale-catch-car-canonical.png` | Active canonical character art — retained |
| `finale-catch-car-v2.png` | Legacy source, not drawn in current game — retained for recovery |
| `finale-catch-car.png` | Legacy source, not drawn in current game — retained for recovery |
| `finale-catch-close.png` | Legacy source, not drawn in current game — retained for recovery |
| `finale-coastal-highway.png` | Active detailed art — retained |
| `finale-earth.png` | Active detailed art — retained |
| `finale-guardian.png` | Active detailed art — retained |
| `finale-homecoming.png` | Active detailed art — retained |
| `finale-orbit.png` | Legacy source, not drawn in current game — retained for recovery |
| `finale-people-canonical.png` | Active canonical character art — retained |
| `finale-plasma-burst.png` | Active detailed art — retained |
| `finale-vortex.png` | Active detailed art — retained |
| `foundry-arena.png` | Active detailed art — retained |
| `foundry-inferno.png` | Active detailed art — retained |
| `foundry-rescue-canonical.png` | Active canonical character art — retained |
| `foundry-rescue-empty.png` | Active detailed art — retained |
| `foundry-rescue.png` | Original retained as alpha matte; canonical art displayed |
| `foundry-warden.png` | Legacy source, not drawn in current game — retained for recovery |
| `furnace-streams-v1.png` | New detailed replacement atlas — integrated |
| `hostile-projectiles-v1.png` | New detailed replacement atlas — integrated |
| `industrial-props-v1.png` | New detailed replacement atlas — integrated |
| `intro-cellar.png` | Active detailed art — retained |
| `journey-cinema-canonical.png` | Active canonical character art — retained |
| `journey-cinema.png` | Original retained as alpha matte; canonical art displayed |
| `omacontra-cover.png` | Active detailed art — retained |
| `omarchy-wordmark.png` | Active detailed art — retained |
| `quattro-bazooka.png` | Active detailed art — retained |
| `quattro-car-canonical.png` | Active canonical character art — retained |
| `quattro-car.png` | Original retained as alpha matte; canonical art displayed |
| `quattro-coast.png` | Active detailed art — retained |
| `quattro-enemies.png` | Active detailed art — retained |
| `quattro-explosion.png` | Active detailed art — retained |
| `quattro-guardrail.png` | Active detailed art — retained |
| `quattro-munitions.png` | Active detailed art — retained |
| `quattro-rally-cinema-canonical.png` | Active canonical character art — retained |
| `quattro-rally-cinema.png` | Original retained as alpha matte; canonical art displayed |
| `quattro-road.png` | Legacy source, not drawn in current game — retained for recovery |
| `reaper-arena.png` | Active detailed art — retained |
| `reaper-sprites.png` | Active detailed art — retained |
| `tidebreaker-arena.png` | Active detailed art — retained |
| `tidebreaker-attacks.png` | Legacy source, not drawn in current game — retained for recovery |
| `tidebreaker-calm.png` | Legacy source, not drawn in current game — retained for recovery |
| `tidebreaker-guardians.png` | Active detailed art — retained |
| `tidebreaker-harpoon.png` | Active detailed art — retained |
| `tidebreaker-natural-waves.png` | Active detailed art — retained |
| `tidebreaker-worlds.png` | Active detailed art — retained |

## Encounter revision — 2026-09-21

The Foundry cabinet scene has been retired. Its detailed arc-rifle asset is now
mounted on the Warden, breaks off under fire, and lands on a platform.
`highway-heart-robot-v1.png` adds the trailer robot's open-heart, armored, and
transformation artwork. Its alpha was regenerated to remove environmental haze;
the game uses opaque articulated armor passes rather than crossfading bodies.
Prompts: `assets/highway-heart-prompts.json` (built-in image_gen).
