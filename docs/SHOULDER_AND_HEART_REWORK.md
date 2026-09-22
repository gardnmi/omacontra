# Shoulder rifle, Iron Heart, and the route to orbit

## Foundry

The Warden's forearm fire and ember fans now start at the actual illustrated
muzzle, including its final discharge. Thin red guide lines are removed.
Weapon glow and mechanical movement announce attacks. New windups do not wait
for old bullets to leave the screen.

The shoulder rifle charges for 1.2 seconds, then remains active until it is
broken. Its fixed sweep takes five seconds each way with smooth turnarounds;
it does not aim at the player. Both rifle owners use the same elastic beam
centerline, and collision follows that centerline. Air dashes pass through it.
The active 180-health mount accepts machine-gun damage throughout the sweep.

Breaking the mount plays the 1.35-second weapon-fall shot. The rifle stays on
the middle platform until collected. Collection starts a seven-second rise
from floor height (630) to 560, 25 pixels below the lower platform tops. Lava
stays at that height for the rest of the encounter. Contact hurts even during
an air dash; all three platforms remain safe. No timed retreat or floor-fire
cycle restores the ground. Tobi and the cabinet are absent from the pickup.

The rescue preserves the lava, moves DHH onto the left platform, and adjusts
Tobi's ejection trajectory to land beside him above the molten floor.

## Highway: Roadblock → Iron Heart

The trailer drops backward toward screen right, away from the player. During
the 3.4-second conversion, cargo panels hinge outward, the torso straightens,
and the robot's feet settle onto the road. The cab continues ahead.

Iron Heart uses new black-and-gold artwork with amber eyes and a cracked ivory
heart. Its second-phase bar has 120 health. Linked arm volleys are followed by
a ground shredder. The armor opens near the end of each 6.4-second cycle;
only the exposed heart accepts damage. Below half health, volleys grow denser.

At 12 health the rooftop bazooka sequence begins. A miss returns to the robot
fight; the next attempt follows the cooldown. A hit destroys the robot with
robot debris. Neither the intact truck nor its trailer reappears. The existing
hill-jump ending remains after victory.

## Story

The harbor dialogue now establishes that the cellar AI is hosted on a space
server. DHH needs a spaceship and takes the ferry toward the launch site;
Tobi keeps the Quattro and looks for a shore route. The Tidebreaker aftermath
identifies the Foundry as the obstacle controlling access to launch.

## Review

```bash
python main.py --cutscene quattro-transform
python main.py --cutscene foundry-disarm
python main.py --cutscene harbor
python main.py --level 2
python main.py --level 4
```

Rendered previews are under `review/shoulder-and-heart/`. The cycle videos are
visual previews; the separate playtest programs exercise normal controls.

- Foundry control run: mount breaks at 20.88s, pickup phase resumes at 22.24s,
  rescue starts at 50.84s, victory at 64.36s with 2 health. Uses slide, double
  jump, and air dash. No health grants or phase skips.
- Highway control run: both phases, heart openings, and the rooftop finisher
  complete in roughly 45 seconds with 2 health. Trace saved alongside previews.
- These are automated control simulations and renderer checks, not a manual
  desktop play session. Human timing and visual feel still need user review.

Robot artwork: `assets/highway-heart-robot-v1.png`. Built-in imagegen prompts,
including the transparent-background correction, are saved in
`assets/highway-heart-prompts.json`.

Validation: all 130 tests passed using `python -m unittest discover -s
 . -p 'test_*.py'` after both reworks and the story update.

## Persistent sweep/lava revision

Current previews: `review/persistent-laser-lava/`. Earlier playthrough timings
above describe the preceding intermittent-beam design. The current control run
and result are recorded in `review/persistent-laser-lava/playthrough.txt`.

Persistent-sweep validation: all 134 tests pass. The control-only run reaches
the disarm at 22.96s and wins at 71.16s with one health remaining. The lava
reaches height 560 and stays there through the ending. The current recording
is `review/persistent-laser-lava/playthrough.mp4`.

## Giant Iron Heart revision

Iron Heart is now 2.35 times its previous size. The road view shows its lower
body; repeated ramps launch the Quattro roughly 600 pixels upward. The camera
follows the car to reveal the upper body and heart, then returns continuously
to the road. Mouse coordinates are converted back into world coordinates on
every update, including while the cursor is stationary during camera movement.

Ramp jumps open the heart. The aerial phase is free of aimed fans, giving a
clear firing window. One ankle-launched shredder per cycle replaces the old
fireball volleys; its traversal speed allows a normal jump to clear the whole
car hitbox. The rooftop finisher holds the car aloft in slow motion so both
DHH and the heart remain visible. Destruction then returns the car to the road.

The gun-and-arms sprite is 45% larger, aligned with the same shoulder pivot;
bullet origins and muzzle flash use the updated barrel length. Canonical head,
body and driver artwork remain in use.

Current control-only recording: `review/giant-heart/playthrough.mp4`.


## Ramp reliability and robot attack revision

- Robot ramps enlarged from 160×40 to 280×100. Swept wheel contact accounts for
  steering and boost, accepts low hops, and latches each ramp after launch.
- Two hand-cannon charges per 7.5-second cycle release downward bolts toward a
  committed position. Flight time to that position is 1.65 seconds. Steering
  escapes a bolt that hits an idle car; the separate shredder remains jumpable.
- Removed displaced rectangular leg/torso crops. One connected body uses a
  planted-foot lean, charge compression and recoil, shared by heart/muzzle coordinates.
- Validation: 139 tests pass, including ramp contact across frame steps, steering,
  boost and small hops; no repeated launch; no high-airborne snapping; and dodge
  escapes. A control-only full run wins with six health in 31.44 seconds.
- Review recording: `review/giant-heart-v2/playthrough.mp4`.


## Spread volleys and jump rendering performance

Each hand-cannon release now sends three downward rays. Their spacing accounts
for the entire car collision rectangle, including travel across its height.
The first volley has a right-side corridor; the second shifts the corridor left.
Shots follow fixed trajectories rather than steering after the player.

The extended reflected sky is rasterized once at renderer construction, then
copied using nearest-neighbor filtering during jumps. Road texture rows below
the camera are skipped. This retains the artwork and body animation.
A warmed 90-frame 1920×1080 Cairo image-surface benchmark at jump height 680
went from 18.0 ms/frame to 4.9 ms/frame. This measures offscreen rendering,
not end-to-end GTK/display frame timing. Ground rendering stayed about 8.8 ms.

Validation: 140 tests pass, including full-car gaps in both fans and a no-damage
steering route between successive volleys. The control-only full run wins with
six health. Recording: `review/giant-heart-spread/playthrough.mp4`.


## Heavy cannon ordnance and returning drones

- Replaced small ember balls with pointed molten armor darts, approximately
  112×43 pixels, plus animated 125-pixel exhaust. Enlarged the cannon ignition
  and charge glow. Reuses cached illustrated projectile and stream assets.
- The damaging core radius is 18 pixels; flame exhaust is visual. Existing
  alternating full-car escape corridors remain tested.
- Phase-two drone reinforcements start 0.8 seconds after transformation and
  recur every 7.5 seconds, with at most two active. Drones enter at the current
  flight altitude; offscreen drones defer their charge until visible.
- Control-only playthrough wins with five health in 31.28 seconds. A warmed
  1080p offscreen high-jump draw with three darts and a drone averages 5.19 ms.
- Recording: `review/giant-heart-heavy/playthrough.mp4`.

## Truck breakup and robot deployment polish

The 3.4-second transition now has staggered engine blasts, diving cab motion,
textured metal fragments, tumbling wheels and a drifting smoke trail. The trailer
still falls backward. Its two armor panels hinge outward while the folded robot
pose deploys, followed by extension to full height and grounded pressure plumes.
A short steam release masks the folded-to-standing pose change.

Combat adds stronger weight shifts and charge/recoil motion, rotating wheel hubs
clipped within the original sockets, and timed shoulder steam vents. Shared body
geometry still drives the heart target and cannon origin. No rectangular limb
slices are displaced. The existing jump-sky cache and shell caches remain intact.
Review: `review/giant-heart-unfold/playthrough.mp4`.
