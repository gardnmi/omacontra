# OMACONTRA — campaign proposal

Status: five playable encounters, including the Black Moon finale first pass. The three-guardian revision below supersedes the original single-wave encounter outline. Reviewed 127 unique wallpapers found in the installed Omarchy theme collections (220 paths before deduplication). These are source references; final levels retain the existing detailed Contra-style pixel art.

## Premise — revised wine-rack portal story

Keep the satirical setup: everyone is watching frontier labs for AI doom. Meanwhile Tobi invites DHH into his wine cellar to show him the server he built into a wine rack.

> TOBI: Come look at the server I built.
> DHH: In your wine rack?
> TOBI: Perfect temperature. Plenty of space. Watch this.

The demonstration opens a portal. Both men are pulled into the server, but their connections separate. DHH wakes alone in the Reaper wallpaper. Tobi lands elsewhere. The worlds are the server's wallpaper environments made physical; the Watcher treats the two users as intruders.

The mission is to escape the server, then shut down the experiment from the real cellar. Neither protagonist knows the whole route. Tobi's confidence drives their first escape attempt; the ocean forces them to change plans.

All story scenes use the Quattro cinematic language: a wide illustrated strip surrounded by black, short dialogue below, deliberate cuts, local animation, and an expansion into the playable arena. Preserve character proportions; no vertical squeezing to fit the strip.

DHH carries the on-foot action. Tobi drives and investigates a parallel route after the harbor. Their radio conversations connect the chapters while keeping the player with DHH.

## Main route

### 01 — The Reaper (existing encounter)

Reference: `harbordark/backgrounds/HBG3.png`.

DHH wakes on the steel floor, calls for Tobi, and notices the Reaper moving. The first fight begins before he understands where he is. Defeating the guardian opens a maintenance route to the coastal environment. Its red eye can briefly show the final villain's iris pattern (future visual foreshadowing).

Keep the existing movement-focused battle: machine gun, slide, double jump, air dash.

### 02 — Quattro Run (existing encounter)

Reference: `tokyo-night/backgrounds/1-quattro.jpg`; `0-winding-road.jpg` supports establishing shots.

DHH finds Tobi again by the Quattro.

> TOBI: DHH! Found this sweet Quattro.
> Hop in. I think I know how to get us out.
> DHH: We have company.

The truck is the Watcher's pursuit vehicle. Damaging its trailer uncouples it;
the cargo drops back away from the Quattro and unfolds into Iron Heart, a
black-and-gold robot with a cracked ivory heart. Arm volleys and a ground
shredder precede a chest-opening firing window. Closed shutters block damage.
The rooftop bazooka finishes the robot, then the existing hill jump carries
them toward the harbor.

At the harbor Tobi reveals that the wine-cellar AI runs on a space server.
They need a spaceship, and the launch site is across the water.

> TOBI: The cellar AI is running on a space server.
> DHH: Then we need a spaceship.
> TOBI: The launch site is across the water.
> DHH: I take the ferry. You find a way in from shore.
> TOBI: I will meet you at the launch site.

Tobi keeps the Quattro and takes the shoreline route. DHH boards the cargo
ferry. The Tidebreaker aftermath establishes that the Foundry controls access
to the launch facility. This is a deliberate split with a rendezvous.

### 03 — Tidebreaker (recommended next level)

Reference: `kanagawa/backgrounds/1-kanagawa.jpg`.

DHH climbs onto the cargo ferry alone; Tobi checks in by radio from the shoreline. The sea freezes into the recognizable Great Wave composition for a beat. Then its foam fingers close around the vessel. **The wave itself is the boss.** A dark, swirling knot inside it provides a readable machine-gun target.

- **Phase 1: learn the sea.** Foam claws strike clearly marked deck positions. Low water surges require jumping; overhead claws leave a slide route. The deck remains level while the player learns these attacks.
- **Phase 2: hold the deck.** A slow, signaled roll raises one side of the ferry. DHH shoots crusted locks off a deck-mounted harpoon while avoiding attacks. DHH triggers the restored harpoon, pinning the wave and exposing its knot. Tobi radios information about the power fluctuations from shore. One new arena behavior at a time; no unpredictable slippery controls.
- **Phase 3: break the crest.** The wave curls over the ship. Three deliberately spaced beats combine jump, slide, and a final double jump through a foam opening. Surviving the sequence gives a generous final firing window. Failed cycles repeat with damage rather than an instant reset.

Updated progression: destroying the wave reveals Black Coat on the right and Dead Orbit on the left simultaneously. Both must fall to complete the crossing; the first defeat shifts the dockyard into its orbital background.

Potential exchange:

> DHH: You said it was a background.
>
> TOBI: It was.

Fairness: preview deck movement; keep the player silhouette visible against the water; never require an air dash immediately after consuming it; reserve a safe route when attacks overlap. First build should prove one satisfying wave strike and one deck movement before adding phases.

### 04 — The Foundry

Reference: `ristretto/backgrounds/3-industrial-moon.jpg`. `harbordark/backgrounds/HBG4.png` can inform machinery detail without replacing the selected skyline.

The ferry docks at the factory manufacturing the Watcher's guardians. DHH
faces the Furnace Warden on a loading platform beneath the orange moon. Tobi
radios that he has found another way in; his shore route leads to an elevated
service road, and he has kept the Quattro.

**Current playable revision:** the supplied black/olive, angular mech is now
the Inferno Warden, engulfed in flames and venting steam. DHH fights throughout
the encounter. Traveling bullet curtains change the height of their open
bands; homing embers commit after a short pursuit; furnace sweeps allow a
slide route; forward lunges force repositioning. Bullet-safe air dashes,
double jumps, and slides provide complementary escapes. Movement attacks
wait for projectile lanes to clear. No tactical instruction overlays appear.

The Warden's shoulder rifle fires a persistent electrical beam after a short
charge. It sweeps slowly across the arena and back (five seconds each way),
independent of DHH's position. The beam uses the same bending lasso centerline
and electrical strands as DHH's rifle. Air dashes pass through it; its active
mount takes machine-gun damage. Forearm attacks continue with more breathing
room so the beam remains the main obstacle.

Breaking the 180-health mount drops the rifle onto the middle platform.
Collecting it immediately starts a seven-second lava rise. The lava covers the
floor permanently, stopping just below the lower platforms. It never recedes,
including during the rescue ending. DHH must stay on and move between the
platforms while using the stolen rifle to finish the Warden. The rescue ends
with DHH and Tobi on the left platform above the lava.

**Rescue ending (implemented):** depleting the health bar does not kill the
Warden. It staggers, opens its furnace doors, and starts a catastrophic final
discharge. The familiar black cinematic strip closes around the same arena.
DHH is about to be overwhelmed when Tobi launches the Quattro from the high
service road into the furnace. Impact ejects Tobi clear, followed by a fast
combined car/boss explosion. Tobi lands beside DHH; both survive and the car
stays destroyed. Combat is suspended for this payoff, with no surprise QTE.

> DHH: You could have used the door.
>
> TOBI: It was locked.

Production stops, exposing the tower route to Black Moon. With the Quattro
lost, they continue on foot. The original crane/conveyor/hydraulic-lock idea
is deferred; it is not part of this playable pass.

### 05 — Black Moon: The Last Connection (implemented first pass)

This replaces the gravity-platform Black Moon and separate Watcher ending.
References: `nord/backgrounds/0-black-moon.jpg`, the user's cream shuttle/red
exhaust wallpaper, and the astronaut holding a luminous jellyfish wallpaper.

Tobi discovers that the cellar rack is a terminal: the AI core runs in orbit.
The Foundry controls access to the launch facility. After losing the Quattro,
they find a shuttle with one working seat. DHH boards; Tobi stays behind.

> DHH: One seat.
> TOBI: Go. I will find another way.
> DHH: Your last ride exploded.
> TOBI: I will find something faster.

The shuttle climbs through darkness with long red exhaust. The finale is a
fullscreen top-down shooter: DHH in a spacesuit below, the AI above against the
black moon. WASD/arrows move freely, fire shoots upward, Shift thruster-dashes.

1. The enclosure: destroy two wrist nodes on the empty astronaut suit.
2. The intelligence: the released jellyfish fires rings, aimed fans and curtains.
3. Containment failure: denser versions combine into the last assault, retaining
   physical gaps, phase-change clearing and periodic recovery windows.

The jellyfish collapses into the original blue portal. DHH is pulled through
and falls into daylight, landing in a yellow Lamborghini driven by Tobi.

> DHH: You found another way.
> TOBI: You can fix anything.

The car speeds away. OMACONTRA / THE END.


## Tidebreaker first-pass scope and review checklist

Implemented:

- Direct launch with `python main.py --level 3`.
- Reaper victory → Enter → Quattro; Quattro victory cinematic → Enter → harbor split → Tidebreaker.
- Cellar demonstration, portal, separation, awakening, and harbor scenes in the cinematic strip style.
- Detailed generated ocean/deck artwork and two-frame water attack sprites.
- Existing run, machine gun, double jump, slide, crouch, and air dash.
- Low surge (jump), overhead sweep (duck/slide), targeted collapsing crest (move out of the marked lane).
- Three health phases, paced cycles, exposed core windows, six player health points.
- Small deck heave in later phases, rain, foam motion, opening/core lighting, wave-break ending and radio check-in.
- Reset/pause/skip/close behavior and standalone simulation/render regression tests.

Still proposed, not implemented:

- Elaborate ferry arrival/landing animation, radio portraits, custom sound/music, and a more elaborate water-collapse finale.
- Playable Tobi shore route; further finale art and balance polish.

Review priorities: does DHH read against the ocean; do the water attacks communicate their collision area; is the fire window long enough; do dialogue and strip-to-game transitions flow; does the third phase remain fair? Keep later systems out until these fundamentals feel good.

## Other strong candidates

- **Coppernight castle + glowing-eyed katana character:** rooftop duel with a human-sized swordsman; visible parries deflect sustained fire, attacks expose recovery windows. Excellent alternate if we want a precision duel before the large-scale wave. References: `coppernight/backgrounds/japanese-castle-pixel-digital-art.jpg`, `Character with Glowing Eyes and Katana.jpg`.
- **Miasma crowned figure:** a silent cloth-and-stone monarch. Fabric becomes walls and fists; damage cracks the crown. Strong ominous optional encounter. Reference: `miasma/backgrounds/02-crowned.jpg`.
- **Amekoji train station:** an empty platform becomes a mechanized train boss; doors reveal weak points, warning lights announce passing carriages. Reserve for a later campaign so it does not repeat the Quattro vehicle encounter immediately. Reference: `amekoji/backgrounds/2825711.png`.
- **Harbordark tower:** lift-platform siege against a building that unfolds around the player. Could replace the Foundry if the existing Reaper's architecture should dominate the campaign. Reference: `harbordark/backgrounds/HBG4.png`.
- **Matte Black ship at sea:** alternate cinematic reference for the sea chapter, especially a moonlit opening. Reference: `matte-black/backgrounds/0-ship-at-sea.jpg`.
- **Retro-82 gateway:** visual reference for transitions between wallpaper worlds. Reference: `retro-82/backgrounds/4-gateway.jpg`.

Plain logos, abstract gradients, portraits, and soft scenic wallpapers are generally stronger menu/interlude references than main boss arenas.

## Art and pacing rules

- Preserve each wallpaper's signature composition, silhouette, and palette. Build separately animated foreground, arena, boss, and distant scenery; do not simulate action by stretching a flat image.
- Translate every world into the same detailed pixel-art treatment as the Reaper and Quattro. Keep DHH's proportions and readable projectile language consistent.
- Every boss gets its own movement, attack shapes, sound identity, and destruction sequence. No reused scythe disguised by a color change.
- Strength comes from weight: purposeful anticipation, fast strikes, convincing recoil, debris that remains destroyed, and short decisive finishers.
- Use the cinematic strip for concise openings and exits. Establish the wallpaper composition, then visibly bring it to life.
- Keep the primary machine gun. Arena mechanics provide variety before additional weapon systems expand the scope.
- Build Tidebreaker next; treat the remaining route as a story outline until its first encounter feels good.

## Tidebreaker revision — implemented encounter

The three wave phases above are playable: level-deck learning, signaled roll
with two shootable harpoon locks and **E** to pin the knot, then the spaced
jump/slide/double-jump crest cycle. A missed cycle causes normal damage and
repeats. A clean cycle grants six seconds of exposure. Health gates at 80 and
40 prevent skipping the arena mechanics with sustained fire.

The ocean animates across its full width. Targeted swells travel from the wave and rear up before collapsing,
low surges build at its foot, and hollow breakers leave a slide route beneath their lips.

Destroying the wave triggers a five-second reveal, clears hazards, and grants
one health point (maximum six). **Dead Orbit enters on the left and Black Coat
on the right at the same time.** Their ranged attacks can cross, but charges
and pressure drops wait for projectile lanes to clear. Both expose their cores
during recovery. Each has independent health and death animation; only both
being defeated ends the chapter. The first defeat reveals the orbital harbor.

These are provisional boss names, not claims about the original wallpaper
characters. Tobi's shore-power route and DHH's uplink route converge at the
Foundry in the next planned chapter. Restart resets the complete crossing.

Foundry armored opening: slide sweep → double-jump barrier → flood plus delayed
vent → air-dash wall → targeted vent → bullet curtains. Recovery is 0.65 seconds;
the rifle cinematic still waits for all opening attacks to clear.
