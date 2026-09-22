# Eye storm and DHH weapon polish — 2026-09-22

Generated with the built-in imagegen tool. Project assets:

- `wyrm-eye-comet.png`: cached at 160×64, drawn about 72 pixels long. The bright head follows the actual projectile collision point; its decorative tail is not damaging.
- `dhh-weapon-v2.png`: replaces the old horizontal arm cluster with a bent elbow and compact rifle. The shoulder anchor is (180,410), barrel end (1490,410), scale .035. Both rendering and bullets use this geometry. Original artwork remains archived.

Eye volleys alternate between the two animated eye anchors. The charging eye matches the firing eye. Phase-two lances lock their origin and target on release. Ledge pressure warns the occupied platform for 1.1 seconds, then erupts after another .25-second growth period. It never follows the player to their next platform. Wide eruptions do not pause the ordinary eye attack schedule.

Sound additions (`eye_charge`, `eye_shot`, `eye_lance`, `storm_hit`) use the existing licensed wind and thunder recordings, trimmed, filtered and enveloped by `tools/build_wyrm_sounds.py`. No periodic laser loop or metallic hit sample. Provenance remains in `audio/library.json` and `audio/sources/README.md`.

## Projectile prompt

Create one production-ready transparent-background game VFX sprite, landscape 1536x1024. A single storm-dragon eye projectile travelling RIGHT, centered horizontally around y=512. High detail dark fantasy pixel art, matching a realistic black-scaled Eastern dragon with luminous ivory white eyes in gray mist. Compact sharp white-hot teardrop core at x=1160 y=512, surrounded by layered pale silver-blue lightning filaments, charcoal storm vapor and curling slate-blue plasma ribbons streaming LEFT to x=160. Rich hand-dithered pixel texture, crisp readable silhouette, strong dark outer edges so it reads against pale gray fog. No solid white slab or giant bloom, no flat vector shapes, no orange, no purple, no scenery, no dragon, no text, no border. One isolated horizontal comet only, generous transparent margins. Genuine transparent alpha background. Asset will be drawn only about 65 pixels long in game; preserve a strong bright head and tapered dark textured tail.

## Weapon prompt

References: `dhh-weapon.png`, `dhh-sprites.png`.

Redesign the isolated arms-and-rifle sprite from reference 1 using the anatomically natural gun holding stance of the standing man in the upper left of reference 2. Output only ONE pair of muscular bare male arms holding a compact black assault rifle pointing horizontally RIGHT, on a truly transparent background, landscape 1536x1024. No torso, no head, no legs, no text. Critical silhouette: rounded left shoulder high at approximate x280 y300, near upper arm descends vertically to elbow x280 y580, forearm bends horizontally right to trigger hand x650 y580. Rifle barrel at y470, below shoulder rather than through the neck. Other hand supports fore-end at x850 y500; far forearm and bicep connect naturally back toward the shoulder at x440 y320, partly hidden behind rifle. Gun stock comes back to x370 y460, muzzle ends x1230 y470. Proportional strong arms, not enormous horizontal bulging biceps, compact rifle not oversized. Black wrist bands, warm skin, intricate crisp 16-bit dark action game pixel shading consistent with reference 2. Preserve transparent background and isolated sprite. The top of shoulder and lower muzzle offset are essential.

## Revision: solid storm ordnance

`wyrm-storm-ordnance.png` replaces the comet and thin-line eruption in gameplay. Built-in imagegen prompt:

Production sprite sheet on genuinely TRANSPARENT background, 1536x1024, exactly three isolated assets in three evenly spaced columns. Dark fantasy detailed pixel art matching a realistic black Eastern dragon in pale gray mist. LEFT COLUMN x40..460 y310..720: one compact spherical storm projectile, obsidian broken shell surrounding a brilliant ivory-white electric core, thin blue lightning crawling over black shards, small trailing sparks to LEFT, ball core center x320 y510, travels RIGHT, clearly readable dark silhouette, NOT a long streak. MIDDLE COLUMN x535..990 y60..950: one tall jagged eruption of solid black volcanic crystal and slate shards rising UP, wide anchored broken rock foot at bottom, narrow jagged spires rising, rich charcoal texture and ivory electric fissures, no flame, no smoke, no beam. RIGHT COLUMN x1050..1480 y310..720: a larger heavy storm projectile, jagged layered obsidian armor around an incandescent white pearl, short compact blue corona, core center x1290 y510, travels RIGHT. Intricate hand-shaded pixel detail, solid dark edge contrast against white mist, limited ivory charcoal slate-blue palette. No orange, no purple, no scene, no text, no labels, no checkerboard. Generous fully transparent separation between three assets. These are premium game sprites, never flat geometric vector art.

Normal volleys: five projectiles at 245 px/sec, 1-second charge and .65-second recovery in phase one. Alternating spread widths retain an aimed center shot. Phase-two heavy volleys replace the eye lance with three larger orbs at 260 px/sec. Eruptions reveal cached stone sprites upward from the platform; collision growth delay and escape warning remain unchanged.

The ultimate charges both eyes and the mouth without projecting a blast. Tobi still interrupts with the car. After pickup, the rising storm starts at world y=780 below the viewport and reaches y=560 over seven seconds. Its visible edge and damaging surface share the same coordinate.
