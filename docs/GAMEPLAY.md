# Gameplay and design notes

## First boss: The Reaper

DHH's on-foot run uses six leg poses with distance-based timing and a small
shared torso/weapon bounce. Running without firing uses a separate six-frame
upper-body carry cycle: bent elbows, shoulder turns, and a rifle tucked upward
near the chest, referenced against Contra's non-shooting run. Holding fire
immediately restores the aiming rig and keeps it steady between shots.
The shared arm/leg cycle lasts 0.60 seconds at normal running speed. The rifle
stays upright for two leg poses, swings forward on the extended stride, then
stays across the chest for two poses before returning. This follows the user's
close-up Contra reference. The long stride lowers the pelvis slightly; the
head stays steady and the soles remain at ground level.
Starting and reversing kick up a short dust puff; slides leave a fading ground
trail. The harbor uses cooler spray colors and
particles follow its tilting deck. Effects are capped at 42 particles and use
cached stamps. Movement speed and collision geometry are unchanged.

Destroy the eye and raven weak points inside the arena to expose the
reaper's core for 11 seconds. Shoot the glowing core inside the wallpaper.
The weak points regenerate; attacks intensify as boss health falls.

The eye fires two rapid volleys of large, glowing skulls; the raven releases two waves of large, fast birds with red trails.
Their attacks start sooner and recur more often as boss health falls. DHH
has a full-body hitbox that shrinks for crouching, sliding, and airborne poses.
The reaper sends
large scythe waves with red trails and launch bursts. Its scythe patterns cycle
through **double jump**, **slide**, and **jump → slide → jump**. A 1.5-second
warning announces each sequence; combo swings are 1.15 seconds apart. Other
attacks pause until the waves leave the arena. Follow the warning,
move out of aimed fire, and keep shooting while running. R starts another
attempt after victory or defeat. The final hit starts a 4.2-second defeat
sequence: the reaper staggers, erupts in explosions, sheds armor fragments,
and dissolves before the victory message appears. Incoming attacks are
canceled during the sequence. Press Enter after victory to continue to Quattro Run.

The intro, title, and fight share one fullscreen window. The scene preserves
its 16:9 proportions on other monitor shapes. Closing the window exits the game.

| Input | Action |
|---|---|
| A/D or Left/Right | Run |
| Space / K | Jump; release and press again for a double jump |
| Shift | Slide on the ground; dash once in the air. Release Shift to rearm |
| S / Down | Crouch |
| Mouse + left button | Aim and fire |
| J / Z | Fire in your facing direction |
| W / Up + J | Fire diagonally upward |
| P | Pause |
| R | Reset encounter |
| Escape / native close | Exit and restore prior workspace |

Sliding lasts 0.42 seconds with a 0.65-second start-to-start cooldown.
Each grounded Shift press triggers one slide; holding it does not repeat. Quick taps and
presses shortly before the slide cooldown ends are buffered for 0.18 seconds. You can fire during a slide
or jump out of it. Its lower profile ducks torso-height shots; low scythe waves
still hit your legs. Tall low waves require the double jump, while the overhead
wave leaves clearance for a slide. Landing restores both jumps.

The cinematic precedes the title screen. Space/Enter advances a story beat;
on the cover it starts combat. P pauses the cinematic; R replays it.
Switching workspaces pauses the game.

## Wallpaper and artwork

The opening transformation reads this **local** installed wallpaper:
`$XDG_CONFIG_HOME/omarchy/themes/harbordark/backgrounds/HBG3.png`
(default config directory: `~/.config`). It does not modify your wallpaper or
redistribute that third-party image. Supply another location with
`--wallpaper /path/to/HBG3.png`. If the original wallpaper is missing, the fight opens directly on its generated
pixel-art stage. The generated boss and arena sprites are bundled.

Cover art was generated from user-supplied DHH/Tobi portraits, skull and Contra
references. `assets/omacontra-cover.png` is the approved title; `cover-v1.png`
is the earlier working title. The replacement DHH poses, reaper poses, mechanical eye, ravens, projectiles,
and arena are generated pixel-art assets. They replace the initial code-drawn
placeholder character. Sprite atlases use magenta transparency decoded at runtime;
frames are rendered with nearest-neighbor sampling. The revised intro uses a generated three-panel cellar/portal/harbor atlas, black cinematic framing, activity lights, and moving data fragments. The cinematic is fictional satire. Its wine cellar is an original
interpretation, not a reproduction of the inaccessible linked X post:
https://x.com/tobi/status/2100955837132939770

## Second level: Quattro Run

Tobi drives the Quattro along a sunset coastal highway while DHH fires from the
rear window. The Roadblock containment truck is on your tail from the first frame.
The scene and vehicles are bundled; the reference wallpaper does not need to be installed.

Start after defeating the reaper with **Enter**, or jump straight in:

```sh
python main.py --level 2
```

- **Mouse + left button** aims and fires; **J/Z** fires backward.
- **Space/K** jumps the car over roadblocks and tire shredders. Release before jumping again.
- **Shift** boosts for 1.2 seconds with a 3.2-second cooldown. Time it to escape a ram.
- A 6.4-second opening cuts from the drivers to the truck pursuing the car, then expands into gameplay. **Enter** skips it. As the truck finishes breaking apart, the highway dissolves into a dedicated front three-quarter rally shot. The car approaches from behind a dirt crest, jumps toward the camera, and flies out of frame to the left, leaving a dust plume before the closing line. Combat does not advance during either cinematic.
- **A/D or Left/Right** moves the car horizontally, including in the air. Releasing the keys holds your position. Boost accelerates your chosen direction; with no direction held it surges forward (left). **P** pauses, **R** resets this level, **Escape** exits.

The truck opens with a telegraphed ram. Choose your targets:

- **MINES:** destroying the low launcher stops ground-running tire shredders.
- **TURRET:** destroying the roof gun stops rocket salvos and mortar strikes,
  including queued attacks. Either weapon can be destroyed first or left intact.
- **ARMORED CORE:** wait for the marked ramps. Stay on the ground as a ramp
  reaches the car to launch automatically, exposing the core for four seconds.
  Core shots deal four times normal damage during this opening. Missing a ramp
  is recoverable; another arrives roughly ten seconds later.

At 30 core health the trailer uncouples and falls behind the truck, toward
screen right. Its panels unfold into **Iron Heart**, a black-and-gold robot.
This 3.4-second transition pauses enemy fire and can be reviewed separately.

The second fight has a fresh 120-health bar and a giant robot whose upper body
is above the road view. Ramps recur every 7.5 seconds and launch the Quattro high
into the air. The camera follows the jump, revealing the robot's upper body and
opening heart. Shoot the heart during these airborne windows. The camera returns
to the road as the car lands; mouse aim remains aligned throughout the movement.

Two charged three-shot downward fans of large molten armor darts leave wide
corridors for the car. Long flame exhaust and a heavy muzzle blast match the robot’s scale.
The second volley shifts the gap left, rewarding steering between the shots. A separate ankle shredder can be jumped.
Drones reinforce every 7.5 seconds during the robot phase, capped at two active.
They charge shots only while visible in the current camera view.
Robot ramps are 280×100 pixels, with swept wheel contact and one launch per ramp;
small manual hops no longer cancel contact. The intact robot leans, compresses
as its cannon charges, and recoils on release. Heart targeting follows that motion.
DHH's gun and arms are resized together to match his torso.

At 12 heart health, press **Space** at the finisher prompt. DHH climbs onto the
roof; **aim at the heart and click** to launch his bazooka. Release held fire
first. A missed shot returns to the robot fight and retries after a cooldown.
A successful rocket destroys the robot; the truck and trailer never reappear.
The getaway jump remains in the ending cinematic.

Review the transformation without playing:
`python main.py --cutscene quattro-transform`

This first pass uses generated pixel-art vehicles and scenery with the existing
DHH body and rotating rifle assets. The distant coastline stays fixed. The asphalt scrolls with perspective, and the near rocks and bushes move together at 1.65 times road speed. Reflected texture edges keep the foreground loop continuous. A separate transparent guardrail, lane markings and road flecks scroll independently;
spinning wheel hubs, suspension, boost exhaust, dust, headlights, and sparks animate during play. The default road speed is 700 pixels/second; boost raises it to 1,150.
Generation prompts are recorded in `assets/quattro-prompts.json`.

## Development

- `src/omacontra/ui/story.py`, `src/omacontra/ui/art.py`: cinematic timeline and drawing.
- `src/omacontra/stages/reaper/combat.py`: reaper simulation, independent of GTK/Hyprland.
- `src/omacontra/stages/highway/chase.py`, `src/omacontra/stages/highway/chase_art.py`: Quattro simulation and rendering.
- `src/omacontra/stages/highway/chase_cinema.py`: opening and victory panel framing; presentation only.
- `src/omacontra/stages/reaper/battle_art.py`: boss, character, and effects rendering.
- `src/omacontra/boss_app.py`: fullscreen viewport, single-window lifecycle, input and cleanup.
- `main.py`: entry point and offline cinematic export.

```sh
python tools/test.py
python main.py --smoke-test
python main.py --render-preview output/omacontra-intro.mp4
```

Smoke testing requires a live Hyprland session and opens/closes one fullscreen window.
Offline video export requires ffmpeg and refuses to overwrite existing files.

Air dash pauses falling for 0.18 seconds and recharges on landing. It does not grant invulnerability; aim for the gaps between projectiles. Spread volleys lock their aim at the start of each burst, and scythe sequences wait for earlier projectiles to clear.

The eye patrols in a slow orbit, the raven sweeps across the upper arena, and the reaper sways and leans into scythe attacks. Turrets hold position during their warning and burst so the spread gaps remain readable. Their hitboxes and projectile origins move with the artwork.

Each enemy uses its own ordnance: the truck deploys industrial tire shredders and finned rockets; drones telegraph cyan laser shots and lock their aim before firing. Wheel animation preserves stationary tire silhouettes and axle centers, with rotating spoke highlights and traveling tread marks.


## Third level: Tidebreaker (first pass)

```sh
python main.py --level 3
```

After the Quattro victory jump, press **Enter** to reach the harbor. DHH and
Tobi agree to split up: Tobi takes the shore power controls; DHH crosses to the
uplink alone on a cargo ferry. Enter skips the harbor cinematic.

The living wave sends low surges (**jump**), overhead foam sweeps (**duck or
slide**), and a targeted collapsing crest (**move away from the rising water**). After three
attacks its glowing core opens. Aim with the mouse and hold the left button to
fire. The encounter has three wave phases and seven campaign health ribbons.
Existing double jump and air dash controls also work. R restarts the crossing,
P pauses, and Escape exits. Defeating both revealed guardians unlocks the victory cinematic.

The shared story now begins with Tobi demonstrating his wine-rack server. Its
portal pulls both men inside and separates them; DHH wakes in the Reaper arena.
Quattro-style cinematic strips carry the opening, reunion, harbor split, and
sea encounter. The title screen retains the cover artwork.

Review the [campaign and story plan](docs/CAMPAIGN_PROPOSAL.md) for the complete
route, alternative wallpapers, and the distinction between implemented work
and future ideas. Later levels and custom audio remain planned.

`src/omacontra/stages/harbor/tidebreaker.py` owns the encounter, `src/omacontra/stages/harbor/tide_art.py` owns its rendering, and
`src/omacontra/stages/harbor/journey_cinema.py` owns the harbor/crossing cinematics. Tidebreaker reuses DHH's
existing movement and gun through `Fight`, with Reaper AI and node regeneration
disabled. Generated art prompts are in `assets/tidebreaker-prompts.json`.

### Tidebreaker: broadside, undertow, break the crest

1. **Broadside:** the deck rocks from the start. Low surges, overhead curls and
   targeted collapses gather visibly in the water before reaching the deck.
   Three attacks give way to a 3.4-second recovery; the core takes damage throughout.
2. **Undertow:** the roll grows stronger and attacks alternate sides. After
   three attacks recede, the wave rests for 4.2 seconds. No harpoon or interaction
   objective interrupts movement and shooting.
3. **Break the crest:** a large curl surrounds the ferry. A spaced low surge,
   overhead breaker and tall foam wall reward jump, slide and double jump/air
   dash. A clean cycle gives six seconds of recovery; taking a hit gives
   three seconds instead. The core remains damageable throughout the cycle.
4. **Crossfire:** destroying the wave reveals **Dead Orbit on the left** and
   **Black Coat on the right**, together. Dodge the astronaut's locked volleys
   and pressure-ring landings, and the gunman's pistol bursts and rushes.
   Their cores take damage during every attack and recovery. Both must be defeated to finish.

The five-second reveal clears attacks and restores one health point, up to the
current chapter’s health capacity.
Movement attacks are coordinated so charges and slams do not overlap volleys.
The dockyard shifts to its orbital background when the first guardian falls.
R resets the entire crossing and both guardians. Attack labels, arrows, marked
lanes and contextual instructions are absent; water buildup and enemy poses
provide the cues. Review: `review/tide-rework/playthrough.mp4`.

Guardian combat is in `src/omacontra/stages/harbor/tide_guardians.py`; poses, world changes, and reveal
framing are in `src/omacontra/stages/harbor/tide_guardian_art.py`. The sprites preserve the supplied
wallpaper characters in the existing pixel-art treatment. Generated prompts
are in `assets/tidebreaker-guardians-prompts.json`.

## Fourth encounter: The Mist Gate

A pale, mist-covered mountain launch terrace replaces the industrial factory. The reference dragon's huge head approaches from depth: luminous eyes and mouth appear first, then it surges forward through the fog and settles into a slow cobra-like sway. Background lightning branches through clouds; the spaceship remains on a distant stone launch plinth.

Phase one keeps the accelerating 360-degree mouth laser and the double-jump platform circuit. Three slow storm wisps replace the five-fireball double volleys. The wisps have fixed, gently wavering paths and wider dodge gaps. The head pose drives the sprite, glow, mouth target and beam origin together.

Destroy the throat core and collect the fallen arc rifle to enter phase two. A dark, electrically charged storm front rises to the former lava boundary and stays there. Stone platforms remain safe. Alongside wisps, the dragon uses a charged breath lane and an updraft locked to the player's previous platform position. The throat glow and gathering mist are the tells; there are no attack-warning labels or red lines.

The Quattro rescue and elevator departure now share the mist terrace scenery. The car still interrupts the final discharge, Tobi ejects, and both characters land on the safe lower-left platform.

The rejected synthetic bank is no longer selected. `tools/build_wyrm_sounds.py` creates quiet wind and low thunder cues, without repeating laser pulses. Credits and modifications are recorded in `assets/audio/sources/README.md`. The player's established movement and machine-gun sounds remain.

`tools/render_wyrm_preview.py` renders a silent introduction/attack preview to `review/wyrm-mist-preview.mp4`.

## Finale: Black Moon

```sh
python main.py --level 5
```

Enter after the Foundry rescue continues to the 23-second shuttle departure.
DHH walks into the launch-tower elevator, its gates close, and the camera follows
him up to the cockpit walkway. He boards through the hatch before launch; Tobi
stays on the ground-level gantry.
The orbital AI is a luminous jellyfish sheltered in an empty astronaut suit.
Destroy both wrist nodes, then the jellyfish through two escalating phases.

DHH retains the Foundry’s jaw-shaped arc rifle. Holding fire emits a continuous
upward electrical lasso beam that damages the first enclosure node or exposed
AI it intersects. Enemy projectiles remain active; releasing fire stops the beam.

**WASD / arrows** move in two dimensions; **J / Z or left mouse** fires upward;
**Shift** dashes with brief protection and a 1.2-second recharge. The bright dot
on DHH marks the small collision center. **P** pauses, **R** restarts the chapter,
**Enter** skips departure, **Escape** exits. No sound effects.

Victory plays the portal collapse, DHH's fall, and Tobi's yellow Lamborghini
rescue. The revised story is recorded in `docs/CAMPAIGN_PROPOSAL.md`.

## Cutscene review gallery

Watch and scrub the actual in-game scenes without playing any encounters:

```sh
python main.py --cutscene
python main.py --cutscene ending --at 15
```

The scene menu includes the opening, wine-rack story, Quattro intro and jump,
harbor, Tidebreaker aftermath, Foundry intro and rescue, shuttle departure,
and finale. The gallery opens in a normal resizable window without changing
workspaces. Select scenes in the dropdown and drag the timeline to seek.

- **Space**: pause/play; **R**: replay; **Escape**: close.
- **Left/Right**: seek one second; **Shift + Left/Right**: step one frame.
- Speed menu: **¼×, ½×, 1×, 2×**. Seeking pauses playback.
- Playback holds at the end, so it never drops you into combat.

For feedback, report the scene name and timestamp displayed beside the controls.

## Asset quality review

[Visual asset audit](docs/VISUAL_ASSET_AUDIT.md) records the complete asset inventory,
replacement props and effects, before/after renders, and generation prompts.
Render the gameplay review scenes and effects preview without starting GTK:

```sh
python tools/asset_review.py --output /tmp/omacontra-art --video
```

The Quattro health HUD uses six compact, transparent Omarchy service medals.
Folded green ribbons suspend openwork mint Omarchy emblems, with no yellow rim
or solid pendant backing. Lost health ribbons disappear. The 20×32 icons have transparent surroundings and no HUD backing panel.

Campaign health starts at five ribbons. Each cleared chapter grants one extra
maximum-health ribbon for the next encounter: 5 / 6 / 7 / 8 / 9. Entering or
retrying an encounter restores that chapter’s full capacity; retries do not
stack rewards. Direct chapter selection uses the same chapter capacity.
All five gameplay HUDs display remaining health as Omarchy ribbons; lost ribbons disappear.

On-foot life loss plays a 0.55-second backward tumble before respawning DHH
with three seconds of flashing invulnerability. The encounter keeps running;
movement and firing are suppressed during the tumble. The last ribbon still
ends the attempt after the fall. Foundry lava recovery uses a platform.
Car hits retain driving control with a suspension jolt; EVA hits retain thrust
control with suit recoil and an impact flash. Both grant three-second protection.
Review: `review/hit-recovery/recovery.mp4`.

The Quattro's final hit destroys the car with staggered blasts, bodywork debris
and lingering fire/smoke; the retry prompt appears after the initial blast.
Robot ramp launches grant flashing protection throughout descent and for 0.8
seconds after landing. Ordinary jumps do not grant this landing protection.

### Tidebreaker cargo hazard

A low trolley marked **AAA OVERSTOCK / FINAL SALE**, packed with sealed game
cases, breaks its restraints 4.5 seconds into the wave encounter. Deck tilt drives
its acceleration and momentum. Successive phases increase the roll amplitude,
roll frequency and trolley speed cap (220 / 290 / 350 pixels per second).
Jump over the crate; its loose cases and impact sparks are decorative.

End-stop brakes hold the crate during overhead breakers so the game does not
require a crate jump and a duck in the same corridor. Other water attacks and
core firing windows continue alongside the moving cargo. The crate spills its
sealed cases when the wave collapses and is absent from the guardian fight.

The crate is a cached native pixel-art prop; its labels are fictional satire.
Simulation: `src/omacontra/stages/harbor/tide_cargo.py`; artwork: `src/omacontra/stages/harbor/tide_cargo_art.py`.
Review: `review/tide-cargo/playthrough.mp4`.

### Guardian practice

Start directly at Black Coat and Dead Orbit, skipping the water fight and cinematics:

```bash
python main.py --guardians
```

During level 3, **F6** also starts guardian practice. **R** retries the guardian duo with full level-3 health, without replaying the water phase. Launch `--level 3` normally to return to the full encounter.

Review either guardian's face close-up and power-up without playing:

```bash
python main.py --cutscene orbit-enrage
python main.py --cutscene coat-enrage
```

After the 2.8-second enrage cinematic, the surviving guardian fires continuously through specials and windups. Its core stays vulnerable throughout this solo phase; damage openings no longer pause its attacks.

Recent encounter updates: the Mist Gate arrival reveals the shuttle, then the dragon advances through fog (8.6 seconds, Enter to skip). The Reaper introduces a wide low scythe sweep: jump, then air-dash over its length. Black Moon fades from Earth to animated Omarchy ASCII screensaver branding after the enclosure phase; the background persists through the final phase.

Black Moon screensaver uses eight authentic animations exported from Omarchy’s `ttfx` engine, played at 30 background FPS with the original 120 FPS timing. See `assets/screensaver/README.md` for source, licensing, and regeneration instructions. The effects pause with combat and require no runtime terminal process.

After the shuttle launch, Black Moon now has a 14.5-second encounter cinematic: monster reveal, tether check, laser charge, push-off and thruster stabilization. Enter skips the current scene; the fight starts with a 2.25-second reaction window. Preview directly with `python main.py --cutscene encounter`.

Opening music: `assets/audio/omacontra-opening-theme.mp3` (registered in `assets/audio/library.json`). Requires `mpv` for background audio playback. Playback volume is 85%. The track loops through the opening and title screen, pauses with the intro or when its workspace is hidden, restarts with R, and stops on Start or exit. Gameplay and post-Start story scenes use their own tracks.

The last-dive cinematic now uses three dedicated illustrated panels in the same narrow black-screen strip as the harbor scenes, with gentle pans and dialogue beneath. Space gameplay uses `dhh-space-laser.png`, an integrated astronaut-and-weapon pose. `src/omacontra/rendering/space_pose.py` shares the drawn muzzle position with beam collision and emission.

Launch elevator support now uses a dedicated `shuttle-launch-gantry.png` with steel guide rails, braced bays, footings and a hoist head. The last-dive tether panel now has a conventional pistol grip and trigger guard. Black Moon projectile speeds are approximately 8–12% faster, volley intervals are 1.10/.78/.60 seconds across phases, and six-volley recovery pauses are .75/.45/.45 seconds; shot counts, dodge gaps, dash protection and the opening reaction window are preserved.

Final jellyfish phase now has 1,500 HP (previously 500); the preceding exposed phase still takes 750 damage. The launch deck, gantry base and Tobi share the same foreground camera transform; the separate floor-free skyline retains distant parallax.

Intro cover now uses `omacontra-cover-v2.png`: original poses with an industrial harbor/foundry backdrop. Reaper arrival uses the full gameplay view: DHH walks over the actual configured wallpaper for 2.1 seconds, recognizes it at 2.3 seconds, and the wallpaper crossfades into the boss arena from 5.2–6.7 seconds. The first-level HUD includes a readable keyboard legend. Only the Reaper’s scythe waves use new animated violet/cyan energy tendrils (`reaper-energy-wave.png`). Original raven and skull attacks are restored; existing hitboxes and attack timing are retained.

Start confirmation blinks the cover prompt for 2.4 seconds and replaces the theme with an original explosion: pressure crack, turbulent blast, descending bass and a reverberant rumble tail (`assets/audio/omacontra-start-impact.wav`). The cue is generated by `tools/build_start_sound.py`; repeated Start presses cannot replay it.







### Continuous gameplay soundtrack

After Start, the wine-rack demonstration starts a looping playlist, shuffled once for each new run:

1. Off Duty Mercenary
2. Contra
3. The Descent
4. Omacontra Opening Theme
5. Boss Battle Protocol

Each song plays to completion. The playlist continues across scenes, level changes, victory, death and retries. Pause or hiding the workspace pauses playback; closing the game stops it. Direct launches of levels 1–4 also start the playlist. Black Moon replaces it with Omarchy Oligarchy from the rocket boarding cutscene onward. The pre-Start opening theme and Start explosion remain separate. Quattro (Let’s Go, Nerds) is archived and no longer plays. Track sources and order are registered in `assets/audio/library.json`; all MP3s are local.

### Secret title-screen code

On the Press Start screen, tap **Up, Up, Down, Down, Left, Right, Left, Right**. A bright rising metallic chime and Omarchy activation badge confirm unlimited lives. The unlock persists through all five levels and retries for this game session. Hits still trigger the normal reaction and recovery protection, but no lives are deducted; the health HUD shows an infinity emblem. Restarting the application resets the unlock.

Historical gun-audio implementation (now disabled): machine-gun fire streamed `assets/audio/machine-gun-burst.wav`, a sustained CC0 AK-47 recording, retaining its natural automatic-fire rattle. Softened treble, gentle compression and a -34 dBFS peak keep it beneath the music. Credits and original recording are in `assets/audio/sources/`; rebuild with `tools/build_machine_gun_sound.py`. `src/omacontra/audio/weapon_audio.py` uses one SDL2 device with a short audio queue, no per-shot processes. Shooting release, laser use, cutscenes, pause, hidden workspaces and hit recovery silence it. Missing audio fails gracefully.

Player machine-gun visuals use `src/omacontra/rendering/player_gun_fx.py`: three short starburst muzzle poses and pointed ivory rounds with yellow/orange edging, following the supplied Blazing Chrome recording. Shared cached pixel stamps cover the rifle and car gun in levels 1–4, including aimed/airborne poses. Enemy attacks, lasers, damage and fire cadence retain their existing behavior. Player machine-gun audio is disabled; muzzle flashes and bullets remain unchanged.

The water boss and both living guardians take damage throughout active combat, including windups and recovery. Water health is 600; each guardian has 190. Recovery timers still pace attacks but do not gate damage. Phase transitions retain excess damage; reveal/enrage cinematics remain protected.

Historical gunfire tuning (now disabled): the recorded burst played at 88% pitch (about two semitones lower), with stronger 70–240 Hz impacts, reduced upper crack and lighter compression to preserve punch. Peak output is -34 dBFS.

Historical sustained-fire implementation (now disabled) looped an uninterrupted run of recorded rounds, trimmed before the next shot with matched tail endpoints. No burst-end silence or whole-loop fade; it continues until firing stops.

### First encounter sound effects

The Reaper encounter now has 19 soft effects: scythe charge/release, skull volleys,
raven wing beats, armor and core impacts, weak-point destruction/exposure/reform,
DHH jump/landing/slide/dash, hurt/death/respawn, and timed boss explosions/final collapse.
Simulation events in `src/omacontra/stages/reaper/combat.py` drive sound once per action. Impacts are throttled;
invulnerability does not repeatedly play hurt sounds. These hooks apply only to level 1.

`src/omacontra/audio/reaper_audio.py` mixes at most six voices into the shared SDL effects stream.
Important damage/destruction cues take priority over incidental sounds. Individual
asset peaks range from -43 to -28 dBFS; playback adds 5 dB to these effects only,
with a -20 dBFS combined ceiling. Pause, hidden
workspaces, cutscenes, retry and exit discard pending effects without replaying them.
The playlist and continuous bass-heavy gun loop keep their current behavior.
Rebuild assets with `python tools/build_reaper_sounds.py`.

Reaper destruction audio uses non-pitched pressure blasts instead of the earlier
short resonant explosion: weak-point breaks last 1.05 seconds; the killing blow
starts a four-second rolling explosion, followed by a 2.8-second final collapse
at the end of the death animation. Small intervening explosions are quieter.

### Living Reaper arena

`src/omacontra/stages/reaper/reaper_environment.py` animates existing fabric artwork, red caged fixtures,
faint skull-eye furnace light, pipe-joint steam, rear-plane ash and occasional
cable sparks. It draws behind all actors/projectiles and follows simulation
time, so pausing freezes it. Scythe charging brightens the fixtures; defeat
reduces their glow. Smoke and light stamps are cached small surfaces.
Gunfire and encounter effects each received a further 3 dB volume increase.

### Quattro Run sound effects

Stage two has a separate bank of 22 mechanical effects, mixed through the same
SDL effects device. Boost and truck ram use short acceleration
sounds; takeoff/landing use suspension thumps. Mine release, mortar launch,
rocket fans, drone shots and the robot cannon have distinct cues. Each volley
plays once; hit sounds are throttled, and off-screen impacts/spawns are silent.
Damage, drone destruction and truck component breaks use muffled impacts/blasts.
The truck detachment explosion starts immediately, unfolding actuators at 0.65 s,
and the planted locking thud at 2.5 s, matching `src/omacontra/stages/highway/chase_robot_art.py`.
Heart shutters sound only on opening/closing, and the finisher rocket and final
robot explosion have their own effects. The final explosion decays into the
immediate outro. Intro scenes, pause, hidden windows and retries discard stale
effects. No constant engine/drone loop or warning-text beep competes with music.

`src/omacontra/audio/chase_audio.py` configures the shared six-voice mixer; `Chase.sound` and
`src/omacontra/stages/highway/chase_robot.py` supply simulation events without changing combat timing.
Rebuild with `python tools/build_chase_sounds.py` after
building the Reaper effects. Source peaks are -42 to -28 dBFS with the same
+5 dB playback gain and -20 dBFS combined ceiling as stage one.

### Revised weapon/destruction palette and coastal atmosphere

The earlier shared generated thuds are superseded by `tools/sound_palette.py`,
called by both stage sound builders. Kenney's CC0 Sci-Fi Sounds supplies distinct
crunch/low-frequency explosions, electrical shots, energy collapse and thruster
rushes; the CC0 Free Firearm Sound Library supplies recorded Model 12 reports
for the mortar/cannon. Every revised event has three alternating takes. Raven
and robot-head destruction have separate sounds; the player's gun loop is now disabled.
Local source masters and licenses are in `assets/audio/sources/`.

`src/omacontra/stages/highway/chase_environment.py` adds independent drifting cloud wisps, sunset reflection ripples,
coastal haze and twinkling lights, distant birds and roadside dust gusts behind
combat. Cached textures and visibility culling keep the high ramp camera cheap;
all motion uses simulation time and freezes on pause. The sun, cliffs, actors
and collision geometry retain their positions.

Coastal animation fix: the painted wallpaper is now completely stationary above
the road. Separate transparent wisps move above the sun (and in the extended
ramp sky), preventing the clipped-sun seam. Water glints, haze and roadside
gusts are more visible. Pixel regression tests protect the sun at multiple
animation times and camera offsets, and confirm motion freezes with game time.

Coastal visibility pass: transparent sunset cloud silhouettes extracted from the
existing artwork now move 19–26 world pixels/second in repeated banks. The ocean
texture rolls in narrow depth-dependent rows inside the sea mask; distant birds
have a more readable wingbeat. The sun regression remains unchanged. An 8-second
preview is at `review/environment/coast-motion-preview.mp4`.

Two thin transparent sunset-cloud banks now cross the sun at 18 and 25 world
pixels/second. Only cloud pixels move: the disc stays fixed underneath. The
regression check now permits cloud occlusion while requiring every uncovered
sun pixel to remain identical to the original painting.

### Tidebreaker sound and scenery

Level three now uses a dedicated 29-event sound bank: recorded water surges and crashes, cargo movement, distinct guardian weapons, jet movement, impact/death cues, and survivor power-ups. Events share the bounded SDL effects mixer; pause and scene changes discard queued tails. Rebuild with `python tools/build_tide_sounds.py`. Source credits are in `assets/audio/sources/README.md`.

The harbor has animated water, chimney smoke, light reflections, edge spray and deck-anchored rain splashes. Motion uses simulation time and small cached textures. The wave dissolves directly in front of the guardians while DHH remains playable on the same deck; no recenter, transition card, or entrance slide. The second overstock trolley releases in wave two. The two carts exchange momentum on contact and retain separate readable hitboxes.

### Obsidian Wyrm — Mist Gate redesign

The coiled dragon sprite and factory scenery were superseded by the reference-faithful portrait, mist terrace and stone platforms. See the fourth-encounter section above. `assets/wyrm-scene.md` records atlas anchors and rendering details.

### Black Moon sound and orbital scenery

Final-level combat now uses `src/omacontra/audio/finale_audio.py` on the shared SDL device. Ring,
aimed fan, spiral, needle and curtain volleys each play one distinct cue. Thruster
bursts, laser engagement, throttled laser contact, containment-node destruction,
phase releases, damage and defeat have separate cues. `tools/build_finale_sounds.py`
builds three variations per event from the locally credited Kenney CC0 sources.
Effects stay beneath the playlist; pausing clears queued sounds.

Only Earth-phase gameplay enables `src/omacontra/stages/space/orbit_effects.py`: star shimmer, a passing
satellite, distant cloud lightning and a pulse traced from the actual atmospheric
edge pixels. Masks are cached when the renderer is created. Screensaver phases
receive no additional scenery effects. Cosmetic motion uses encounter time, so
it freezes with pause. The added effects measured about 0.15 ms/frame at 1280×720
on this machine, excluding presentation.
# Editable story script

See [GAME_SCRIPT.md](GAME_SCRIPT.md) for the current complete narrative, dialogue,
cutscene timing, gameplay story beats, and ending. Edit that document to propose
story changes; it does not automatically alter runtime dialogue.

### Arcade continue

All final-life deaths now lead to a ten-second continue screen after the death
animation. Enter, Space or R accepts; the two bruised heroes raise their heads,
their eyes gleam, and the current encounter restarts with full campaign lives.
Intro cutscenes are skipped, and guardian retries remain at the guardian fight.
Keys held when the screen appears must be released before accepting. Timeout
plays one finishing impact and displays Game Over; Enter returns to the title.
The countdown freezes when the game is hidden. Portraits are cached and rendered
at native resolution, with source/prompt notes in `assets/continue-portraits.md`.

## Release polish and player menus

**Escape or P** opens a persistent pause menu: Resume, Controls, Options,
Restart encounter, Return to title, Credits, and Quit. Losing focus or leaving
its workspace opens that menu and requires deliberate resume, including during
cutscenes and the continue countdown. Restart/title/quit ask for confirmation;
R requests restart instead of silently discarding the fight. Native window close
still exits normally. Held menu keys must be released before gameplay accepts them.

Options provide separate Music and Effects levels (0–150% of the existing
mix; arrows adjust by 5%). Preferences and personal-best times are atomically
saved to `$XDG_CONFIG_HOME/omacontra/profile.json` (default `~/.config/omacontra/`).
Corrupt/missing preferences fall back to defaults; save failures show in the menu.

Boss defeat retains the authored destruction and ending cinematics. Music briefly
dips beneath the final impact. Stage clear shows an earned medal beside the message
with a short confirmation sound. Advancing carries remaining lives forward and adds
exactly one earned life; it does not refill lost lives. Fresh starts and continues
still restore the encounter's full allotment. The medal does not fly into the HUD.
The final ending leads to results and **Play again / Boss select / Title / Credits /
Quit**. Play again starts level one; boss selection is explicitly practice.

Results show active combat time across attempts, lives lost, continues, restarts,
and no-hit stages. Normal and unlimited-lives personal bests are separate. Practice
runs never replace campaign records. Accepted damage is counted even with unlimited
lives: Lives Lost records each hit that would have consumed a life, while medals
and health stay intact. Hits blocked by invincibility do not count. Music and art credits, including the locally documented sound-source authors,
are available from pause and results.

Movement polish adds landing compression, a short reversal brace, contact shadows,
wet footprints/ripples, and mist displaced on stone-platform landings. Highway
landings compress/rebound the car suspension; boosts and reversals leave short tire
marks. Cargo has deck shadows and independently rattling illustrated game cases.
Heavy Reaper attacks loosen background masonry dust. Mist follows the dragon's
sway. The orbital tether tightens with distance and thrust; no scenery effects were
added to the screensaver phases. Lost ribbons briefly flicker away, successful hits
have warm impact accents, and a shrinking recovery ring marks the final 0.65 seconds
of invulnerability. All decorative effects use encounter clocks and bounded/cached
surfaces, and do not alter combat hitboxes or attack patterns.

### Hardcore mode

Press Start on the title screen to choose Standard or Hardcore. Hardcore keeps the same starting lives and earned ribbons, but losing the last life ends the run immediately: no continue countdown or encounter restarts. Unlimited lives is disabled when selecting Hardcore. Lives carry between stages, with one extra ribbon awarded per cleared stage. Hardcore clear times have their own personal-best record. Play Again repeats the selected mode; returning to the title lets you choose again.

### Final environment detail pass

Reaper pipe flanges gather and shed condensation. A distant fishing boat leaves a
small wake on the highway coast. Harbor runoff falls with gravity even when the
deck tilts. Narrow mist gusts climb the dragon arena's distant cliffs. The orbital
satellite slowly changes attitude and catches sunlight on its panels, only in
phase one. These details use simulation time, fixed small draw counts and existing
cached mist art; pausing freezes them and they never create collision objects.

### Final arcade audio pass

Player machine-gun audio is silent. All remaining effects receive a 10% gain
increase; soundtrack volume is unchanged. Older gun recordings and tuning notes
are retained as asset history, not active playback behavior.

New action cues distinguish double jumps in the Reaper, harbor and dragon fights,
signal Quattro boost and space thruster readiness, accompany the guardians’
reveal, and build during the dragon’s final charge. Readiness cues play once when
a used ability recovers; they do not repeat while ready.
Rebuild these additions with `python tools/build_arcade_details.py`. The full
background music playlist repeats indefinitely after its final track.

Omarchy Oligarchy is reserved for Black Moon. The ordinary looping playlist omits
it; the track starts from the beginning as the rocket boarding/departure cutscene
begins and loops throughout the final level, continuing across deaths and retries.
Returning to earlier stages or starting a new run restores the ordinary playlist.

### Arcade menu polish

Pause, run selection, audio, controls, practice, credits, confirmation and results
share an opaque framed menu with cached stage artwork, strong selection bands,
subtle cursor motion and Omarchy green/cream accents. Results use separate stat
cards and compact earned ribbons; gameplay pause text cannot show through.
Mouse hover selects rows, clicks confirm, and clicking an audio meter sets its
volume. Keyboard controls remain immediate and submenu returns remember selection.

Six original quiet menu cues cover opening, movement, confirmation, back, volume
adjustment and mission completion. Menu audio uses the Effects setting and a
bounded mixer while combat stays paused; hidden windows clear the cues. Final
level music continues across the results menus. Rebuild the sounds using
`python tools/build_menu_sounds.py`.

The regular five-song playlist gets a fresh random order for each new campaign
or practice run, including Play again. Stage transitions, deaths, continues and
encounter restarts keep the current song and order. Songs play in full and the
shuffled list loops. Omarchy Oligarchy stays outside the shuffle, starting at
rocket boarding and continuing through the final battle and results.

### Material-specific bullet impacts

Successful collision callbacks now distinguish the Reaper’s armor and exposed
body, its mechanical eye and raven, truck panels, drones, the robot heart,
water, the guardians’ suit/shell, dragon scales/throat crystal and space
energy nodes/jellyfish. The acquired laser also gives throttled contact feedback.
Each material has three alternating takes, short tails and restrained levels.
Every bullet collision triggers a cue; continuous laser contact is limited to
once per 0.30 seconds. Destruction cues keep priority in the
six-voice mixer. Damage, aiming and collision geometry are unchanged.
Rebuild with `python tools/build_bullet_impacts.py` after other stage builders.

Metal hits use recorded heavy/light metal and panel transients, with hollow
resonances reduced and tails shortened to 60–75 ms. They follow the actual
bullet pattern instead of suppressing alternate impacts.

The Reaper’s eye and exposed body now have dedicated compact bass/crunch
impacts, with a fuller 30–55 ms body instead of a click that decays immediately.
The eye is tighter; the exposed Reaper hits lower. Other target sounds and the
one-impact-per-bullet timing remain unchanged.

The remaining stages now use dedicated weighted impact presets: vehicle armor,
panels, drone and heart; guardian shell/suit and water; dragon core/scales/laser;
and jellyfish tissue/energy nodes. Short bass bodies support distinct crunchy,
energy or wet textures without metallic ringing. Per-bullet timing and laser
contact throttling are unchanged.

### Soundtrack player

Music player is available from Choose your run, Pause and Mission complete.
Select any of the six current soundtrack songs and press Enter (or click) to
play; selecting the same song toggles pause. Left/right plays the previous/next
song. Stop silences the player; Back restores the parent menu and its music.
Selected tracks loop. Previewing pauses the existing music player, preserving
its position, and never changes the campaign shuffle or reserved finale theme.
The music volume setting also controls previews; hidden windows pause playback.
