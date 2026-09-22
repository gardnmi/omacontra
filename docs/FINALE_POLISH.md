# Finale effects and camera sequence

## References researched

- [Housemarque: Nex Machina tips](https://blog.playstation.com/archive/2017/07/06/10-expert-tips-for-dying-slightly-less-frequently-in-housemarques-brutal-ps4-shooter-nex-machina): distinct beam colors communicate different dodge rules, with precise dash timing.
- [CAVE / publisher: Mushihimesama](https://store.steampowered.com/app/377860/Mushihimesama/): intricate dense shot patterns and escalating difficulty.

Our application: visually distinct pearl rings, needle volleys, and spore fans,
all emitted from the jellyfish. Patterns retain physical gaps, phase-change
clearing and recovery time. The bell's idle pulse remains slow; emission flashes
and gently flowing tendrils add activity without rapid pose changes.

## Silent return sequence

- 0–7 seconds: bell ruptures, debris spirals inward, portal forms, DHH is pulled in.
- 7–10: reverse angle, facing DHH with the portal behind him.
- 10–14: wide shot of DHH falling through open sky.
- 14–18: tracking close-up of Tobi accelerating the yellow Lamborghini.
- 18–21: wide catch; the car crosses beneath the falling passenger.
- 21–27: suspension settles, Tobi's final line, car accelerates away.

DHH has no ending dialogue. No sound effects. Tire silhouettes remain attached
to the car; wheel motion no longer rotates cropped patches of bodywork. Seated
DHH uses his existing body artwork with sizing independent of the falling pose.

## Subsequent pacing and camera revision

The reverse-angle shot uses a dedicated foreshortened reaching sprite: feet
recede into the portal, face and hand toward the camera. The Lamborghini stays
in motion after the catch; scenery tracks continuously and the camera widens.

Enclosure nodes now have 450 health each and take 1.5 damage per shot. Phase one
uses pearl rings and committed spore volleys. Release replaces these with pink
curving pinwheels and faster electrical needles; the final phase adds layered
fans and a shorter interval. Periodic recovery and phase-change bullet clearing
remain. Automated pilots reached release in approximately 39–54 seconds.

## Final rescue revision

The ending now lasts 24 seconds. Keep the in-arena portal pull (0–7s), cut directly to the sky fall (7–11s), show Tobi accelerating (11–15s), then use one continuous tracking shot for interception and the coastal drive (15–24s). DHH reaches the passenger seat at 18s; suspension compression, brief tire spray, and an eased camera pullback carry the impact into the drive. DHH remains silent. Gameplay uses a dedicated rear-facing spacesuit sprite. The enclosure breakup renders only on the first release, never on the low-health escalation.

## Orbital spacewalk and dedicated catch art

The combat backdrop is now Earth seen from orbit, based on the supplied blue-Earth reference. The shuttle drifts at the lower right and a flexible visual safety tether connects its winch to DHH's backpack. The tether has no collision or movement restriction; it releases as the portal takes DHH. Combat balance is unchanged.

The homecoming uses `finale-catch-car.png`, two matching full-car poses with the same driver and wheelbase. DHH's landing blends into the illustrated passenger pose, followed by suspension compression and tire spray. The camera tracks the catch and pulls back while the car keeps driving. Preview with `python main.py --cutscene ending --at 15`. Asset prompts and built-in imagegen provenance are in `assets/finale-prompts.json`.

## Surprise rescue revision

Current ending duration: **19 seconds**, superseding previous timelines above.

- 0–7: symmetric vacuum energy burst, then collapse into a stylized black-core
  vortex with tilted accretion arcs. The camera pulls back to fit the effect.
  No truck/ground explosion sprite is used.
- 7–11: DHH falls alone. No driver reveal.
- 11–13: ground approaches; the Lamborghini first enters at 12.45 seconds and
  intercepts DHH at 13. The camera begins tracking its continuing movement.
- 13–19: suspension reaction, rotating clipped rim artwork, scrolling asphalt,
  coastal pullback, then Tobi's line. No pre-rescue dialogue or car close-up.

Review: `python main.py --cutscene ending --at 11`.

Possible next refinements to discuss: a very brief impact hold before the
camera catches up; DHH clinging to the door and looking back at the sky; a
coastal tunnel entrance as the final iris-to-black. Keep Tobi's arrival secret
until the interception and keep the getaway moving throughout.

## Dimensional vortex and coastal destination

Current duration is **22 seconds**. The original surprise interception remains
at 13s. At 13.2–14.4s, a new low three-quarter reaction shot shows DHH gripping
the car while Tobi drives. At 14.4–22s, cut behind the yellow convertible: both
passengers face the Pacific highway and Omarchy skyline. Perspective lane
markings flow toward the camera as the car pulls away. There is no final
dialogue; the requested “fix anything” line has been removed.

The vortex uses illustrated transparent plasma with a lensed upper arch and
foreground accretion disc, plus restrained local filament displacement. It
replaces the thin vector rings while retaining the in-game portal pull.

Preview: `python main.py --cutscene ending --at 12`.
Generated assets and prompts are recorded in `assets/finale-prompts.json`.

## Direct catch-to-rear cut

Removed the front-facing reaction shot. At 13.2 seconds, cut directly from the
completed catch to the rear chase view toward Omarchy. Rear driving duration
is unchanged; total ending duration is now 20.8 seconds.

## Filled plasma rupture and rocket exhaust

Replaced wireframe nova rings/spokes with six blended spherical plasma frames.
The jellyfish stays anchored to its death position and dissolves into the burst,
which then contracts into the existing vortex. Atlas blends preserve opacity.

Departure keeps the wallpaper's twin red wakes, now softer and fading with
distance, with three luminous engine plumes, animated shock cells and engine
glow at the nozzles. Review departure at 9s or ending at 0.5s.

## Cinematic continuity fixes

- Lamborghini uses a single car pose with a revised Tobi face; accelerates entirely offscreen before the rear-view cut at 14.4 seconds. Ending duration is 22 seconds.
- Docked shuttle is three times its previous size, with the upper hull beyond the frame.
- Foundry rescue switches to an empty cockpit at ejection; car debris also uses the empty artwork.
- Quattro gunner uses one continuous upper-body clip, avoiding the shoulder seam while retaining door-sill occlusion.
