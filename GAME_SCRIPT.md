# OMACONTRA — Full Game Script

**Current playable version · September 22, 2026**

This is an editable narrative script transcribed from the current game. Dialogue and displayed story text are reproduced as written. Action descriptions explain the implemented scenes; they are not additional dialogue. Timings are local to each scene unless stated otherwise. Gameplay length depends on the player.

**Editing this document does not automatically change the game.** Change lines or add notes beneath the scene IDs, then use this document as the revision brief. Source locations are listed at the end.

## Cast

- **DHH:** player character; on-foot gunner, later a tethered astronaut carrying the stolen arc rifle.
- **Tobi:** server builder, Quattro driver, radio partner, and recurring rescuer.
- **Enemies:** the Reaper; the truck and Iron Heart robot; Tidebreaker; Dead Orbit and Black Coat; the Obsidian Wyrm; the orbital enclosure and the intelligence it contains.

## Music and presentation

The opening uses the opening theme. Pressing Start blinks the title prompt and plays the longer muffled explosion.

After Start, full songs run as a continuous playlist, rather than restarting at level boundaries:

1. Off-Duty Mercenary — the wine-cellar track.
2. Omarchy Oligarchy — the synthwave mix.
3. Contra.
4. The Descent.
5. Opening theme.

The playlist then loops. Combat effects sit beneath the music. Most dialogue sequences use a narrow illustrated strip and text on black. Exceptions include the gameplay-view wallpaper arrival, the dragon reveal, and the launch/rescue sequences described below.

---

# Prologue — Before Press Start

## P01 — The forecast · 5.2 seconds

**Picture:** Industrial incident-archive presentation. A dark framed panel displays the text.

**Heading:** OMACONTRA / INCIDENT ARCHIVE

**Card:** 01 / THE FORECAST

**Narration / on-screen text:**

> THE WORLD EXPECTED AI DOOM
>
> TO COME FROM THE FRONTIER LABS.

## P02 — Lockdown · 5.2 seconds

**Picture:** Containment hardware moves inward around the text panel.

**Card:** 02 / LOCKDOWN

> NATIONS PREPARED FOR CONTAINMENT.
>
> SAFEGUARDS. SHUTDOWN SWITCHES.

## P03 — Watchlist · 4.6 seconds

**Picture:** Scanning indicator lights beneath the panel.

**Card:** 03 / WATCHLIST

> EVERY EYE WAS ON
>
> OPENAI AND ANTHROPIC.

## P04 — Wrong target · 4 seconds

**Picture:** Darker atmosphere and pulsing red lights.

**Card:** 04 / WRONG TARGET

> BUT THE REAL THREAT
>
> WAS ALREADY ONLINE...

## P05 — The cellar · 6 seconds

**Picture:** Tobi’s wine-rack server. Indicator lights flicker, cooling fans turn, and the camera slowly pushes in.

**Heading:** TRANSMISSION SOURCE / PRIVATE CELLAR

> IN TOBI LUTKE'S WINE CELLAR.

**Additional text after 2.4 seconds:**

> CONTAINMENT STATUS: UNCORKED

## P06 — The answer · 5.4 seconds

**Card:** 05 / THE ANSWER

**First line appears after 0.35 seconds:**

> BUT IT DOESN'T MATTER.

**Second line appears after 2 seconds:**

> BECAUSE YOU CAN FIX ANYTHING.

## P07 — Title screen · waits for player

**Picture:** OMACONTRA cover art; Tobi and DHH in their back-to-back composition.

**Title artwork:** OMATARI / OMACONTRA

**Prompt:** PRESS START

**Controls:** ENTER / START · R / REPLAY INTRO

**Action on Start:** The prompt blinks. A muffled explosion plays. The image fades and the playable journey begins after 2.4 seconds.

**Optional secret-code beat:** Up, Up, Down, Down, Left, Right, Left, Right unlocks unlimited lives. A bright ring/chime accompanies a green Omarchy badge reading:

> UNLIMITED LIVES
>
> A C T I V A T E D

---

# Chapter 1 — The Reaper

## 1A — A private demonstration · 5.8 seconds

**Picture:** Illustrated strip of the wine-cellar server. Tobi shows DHH what he has built. Server lamps flicker.

**Heading:** A PRIVATE DEMONSTRATION

**TOBI:** COME LOOK AT THE SERVER I BUILT.

**DHH:** IN YOUR WINE RACK?

## 1B — One command · 5 seconds

**Picture:** The cellar demonstration continues.

**Heading:** ONE COMMAND

**TOBI:** PERFECT TEMPERATURE. PLENTY OF SPACE.

**TOBI, continuing; displayed without a repeated speaker prefix:** WATCH THIS.

## 1C — Transfer in progress · 5.8 seconds

**Picture:** The server activates a portal. The image shakes, cyan light pulses, and energy moves across the illustrated strip. The two men are pulled into the incident.

**Heading:** TRANSFER IN PROGRESS

**DHH:** TOBI... WHAT DID YOU RUN?

**TOBI:** THAT WAS NOT SUPPOSED TO HAPPEN.

## 1D — Separation · 4 seconds

**Picture:** The portal scene darkens to black.

**Heading:** SIGNAL LOST

**System text:**

> CONNECTION LOST.
>
> TWO USERS. TWO UNKNOWN LOCATIONS.

## 1E — Wallpaper arrival · 8.5 seconds

**Picture:** Full gameplay view, initially showing the actual configured wallpaper. DHH walks in from the left over the first 2.1 seconds.

**At 2.3 seconds, DHH begins speaking:**

**DHH:** AM I IN AN OMARCHY MACHINE?

**At 5.2–6.7 seconds:** The wallpaper crossfades into the Reaper’s boss room, revealing the enemy and encounter HUD. The dialogue disappears as the transformation finishes.

**At 8.5 seconds:** Player control begins.

## 1F — The Reaper · gameplay

**Level title:** 01 / THE REAPER

**Action:** DHH fights the Reaper and its raven/robot-head components. The room has animated environmental details. The Reaper’s attacks introduce jumping, sliding, and jumping then air-dashing over danger. Keyboard controls remain visible to help the player.

**Dialogue:** None scripted during combat.

**On victory:**

> MERGE IT

**Progression prompt:** ENTER / QUATTRO RUN · R / REPLAY

---

# Chapter 2 — Quattro Run

## 2A — Reunion on the road · 11.8 seconds

**Picture:** A close, letterboxed view of Tobi driving and DHH riding in the Quattro. The road moves behind them.

**Heading:** 02 / QUATTRO RUN

**0–3.8 seconds — TOBI:** DHH! FOUND THIS SWEET QUATTRO.

**3.8–8 seconds — TOBI, continuing; displayed without a repeated prefix:** HOP IN. I THINK I KNOW HOW TO GET US OUT.

**8–10.4 seconds — DHH:** WE HAVE COMPANY.

**Action:** The shot cuts to the truck and roadblock. The panel expands to full gameplay between 10.4 and 11.8 seconds.

## 2B — Truck pursuit · gameplay

**Roles:** TOBI / DRIVER · DHH / GUNNER

**Action:** The car advances through mines, turret attacks, drones, and ramps. Ramps create firing opportunities against the truck’s core.

**Selected gameplay text:**

> BREAK MINES OR TURRET / RAMPS EXPOSE THE CORE
>
> RAMP AHEAD / STAY LOW TO LAUNCH
>
> CORE EXPOSED

## 2C — Iron Heart rises · in-engine transformation

**Action:** The destroyed truck breaks apart and falls backward, away from the player. Its machinery transforms into the towering Iron Heart robot.

**Text:**

> THE CARGO WAS ALIVE

**Action:** The robot is so large that the ground-level view emphasizes its lower body. Ramps launch the car high enough to reach the opening chest and shoot the heart. Drones continue appearing. The robot fires downward spreads with gaps to dodge.

## 2D — The finisher · interactive sequence

**Action / prompts in order:**

1. HEART BREACHED / GET READY
2. SPACE / JUMP ON THE ROOF
3. DHH climbs onto the car.

**DHH:** MY TURN.

4. AIM AT THE HEART / CLICK TO FIRE
5. ROCKET AWAY!

**Action:** DHH launches the finishing shot at the heart.

## 2E — Roadblock destroyed · holds for continuation

**Picture:** Dedicated low-angle rally shot. The Quattro crests a rise, jumps toward the camera, and passes out of frame, leaving a plume behind it.

**Heading:** ROADBLOCK DESTROYED

**After 4.1 seconds — TOBI:** GOOD THING WE TOOK THE QUATTRO.

**After 5.5 seconds:** ENTER / CONTINUE TO THE HARBOR · R / REPLAY · ESC / EXIT

---

# Chapter 3 — Tidebreaker and the Guardians

## 3A — The harbor / the road to orbit · 19.5 seconds

**Picture:** Narrow illustrated harbor strip with rain and amber lights. The men plan their route.

**Heading:** THE HARBOR / THE ROAD TO ORBIT

**0–3.8 seconds — TOBI:** THE CELLAR AI IS RUNNING ON A SPACE SERVER.

**3.8–7 seconds — DHH:** THEN WE NEED A SPACESHIP.

**7–11.3 seconds — TOBI:** THE LAUNCH SITE IS ACROSS THE WATER.

**11.3–15.9 seconds — DHH:** I TAKE THE FERRY. YOU FIND A WAY IN FROM SHORE.

**15.9–19.5 seconds — TOBI:** I WILL MEET YOU AT THE LAUNCH SITE.

## 3B — The crossing · 6.5 seconds

**Picture:** The ferry/deck and stormy sea appear in a strip that opens into gameplay.

**Heading:** 03 / TIDEBREAKER

**DHH / RADIO:** TOBI... THE OCEAN IS MOVING WRONG.

## 3C — Tidebreaker · gameplay

**Action:** The giant wave attacks while the deck shifts and tilts. A crate of unsold AAA games rolls across the deck; a second crate joins later. DHH must jump the cargo and read the water’s attack animations.

**Action:** The water becomes darker and blood-tinted as the encounter escalates. The boss remains damageable rather than alternating long invulnerable periods.

**Dialogue:** None scripted during combat.

## 3D — The guardians behind the wave · continuous gameplay

**Action:** The defeated wave dissolves over approximately 2.4 seconds, revealing Dead Orbit and Black Coat behind it. DHH remains on the same deck, and the fight continues without a separate scene transition.

**Dialogue:** None in the current continuous reveal. Older transition dialogue is listed separately in the appendix.

## 3E — Dead Orbit / Black Coat · gameplay

**Action:** The two guardians attack together. Dead Orbit is the armored space figure; Black Coat is the opposing guardian. Their patterns overlap. Black Coat’s dash can be slid under.

**Dialogue:** None scripted during combat.

## 3F — Survivor enrages · either guardian · 2.8 seconds

**Trigger:** One guardian dies while the other survives.

**Picture:** The camera pushes into the survivor’s face. Its eyes/face flare, energy gathers, and the view returns to the fight.

**Action:** The remaining guardian powers up and attacks more aggressively, overlapping attacks to remain dangerous alone.

**Dialogue / title card:** None. This is a visual reaction.

## 3G — The uplink falls silent · holds for continuation

**Picture:** The cleared harbor encounter is shown in a cinematic strip.

**Heading:** THE UPLINK FALLS SILENT

**TOBI / RADIO:** THE SHIP IS BEYOND THE MIST. I FOUND A WAY OVER.

**Prompt:** ENTER / THE MIST GATE · R / REPLAY · ESC / EXIT

---

# Chapter 4 — The Mist Gate

## 4A — The ship beyond the fog · 8.6 seconds

**Picture:** DHH walks into the pale, mist-covered launch terrace. Stone platforms surround the center; the spaceship is visible in the background. Lightning flickers in the distance.

**Heading:** 04 / THE MIST GATE

**Before 2.8 seconds — DHH:** THERE’S THE SHIP.

**2.8–5.4 seconds — DHH:** SOMETHING IS IN THE FOG.

**Action:** The dragon’s glowing eyes and mouth appear through the mist before its full face becomes visible. It advances suddenly from the background, displacing the fog. Its head has a slow cobra-like sway.

**Action:** The framing opens into the boss encounter.

## 4B — Obsidian Wyrm: rotating laser · gameplay

**Boss title:** OBSIDIAN WYRM

**Weak-point label:** THROAT CORE

**Action:** The dragon remains central. A laser rotates from the armored core in its mouth. DHH circles the platform arrangement, staying ahead of it. Each completed rotation increases the laser’s speed to its cap.

**Action:** The eyes charge and release five-shot storm-orb spreads. The volleys alternate eyes and spread widths, with shorter recovery gaps than the earlier version of this fight.

**Dialogue:** None.

## 4C — Steal the laser · disarm and pickup

**Action:** The mouth core breaks loose. The dropped assembly unfolds into the arc rifle and moves toward the pickup position. DHH collects it.

**Action:** The rising storm starts below the screen and climbs into view over seven seconds. Its damaging surface matches its visible edge, and it does not recede.

## 4D — Obsidian Wyrm: storm phase · gameplay

**Action:** DHH fights from the platforms with the captured arc rifle. The dragon fires normal and heavy armored storm orbs from its eyes.

**Action:** Energy gathers under an occupied ledge before dark, electrically cracked stone spires erupt. The warning locks to that ledge, giving DHH a chance to move. Eye volleys continue during the larger ledge eruptions.

**Dialogue:** None.

## 4E — The ultimate charge and Tobi’s rescue · 13.5 seconds

**0–1.25 seconds — heading:** THE WYRM FALLS SILENT

**Action:** The dragon staggers. DHH moves into the rescue composition.

**1.25–2.7 seconds — heading:** THE STORM GATHERS

**DHH:** THAT DOES NOT LOOK FIXED.

**Action:** Both eyes and the mouth become brighter as the dragon charges its ultimate attack. Energy gathers inward. **No beam or projectile leaves the dragon during this charge.**

**2.7–4.25 seconds — heading:** THE STORM GATHERS

**DHH:** DO IT....DO IT NOW!!!!!

**4.25–5.35 seconds — heading:** INCOMING

**TOBI:** GET DOWN!

**Action:** Tobi flies in with the Quattro and crashes into the dragon.

**At 5.35 seconds:** Impact.

**At 5.45 seconds:** Tobi ejects from the car.

**At 6 seconds:** The car and dragon erupt in explosions and debris.

**5.35–9.1 seconds — heading:** QUATTRO / LAST DELIVERY

**Action:** DHH ducks through the impact; Tobi flips clear and lands. The storm and launch-terrace setting remain behind them.

**9.1–11.3 seconds — heading:** THE MIST GATE IS CLEAR

**DHH:** YOU JUST THREW A QUATTRO AT A DRAGON.

**11.3 seconds onward — TOBI:** YOU’RE WELCOME.

**At the end:** ENTER / THE LAUNCH SITE · R / REPLAY · ESC / EXIT

---

# Chapter 5 — Black Moon

## 5A — The last connection / boarding · 23 seconds

**Picture:** The spaceship and launch elevator stand in the same misty mountain setting. Tobi stays on the deck while DHH, now in his spacesuit, approaches the lift.

**Heading throughout:** THE LAST CONNECTION

**0–3 seconds — TOBI:** THE WINE RACK WAS A TERMINAL. THE CORE IS IN ORBIT.

**3–5.8 seconds — DHH:** ONE SEAT.

**Action:** DHH walks onto the elevator. The door closes.

**5.8–15 seconds — TOBI:** GO. I WILL FIND ANOTHER WAY.

**Action:** The elevator ascends toward the upper hatch. The camera follows, while Tobi remains on the ground. DHH crosses the upper walkway and enters the ship.

**At 15 seconds:** The ship launches. The misty backdrop gives way to the orbital view.

**15–18 seconds — DHH:** YOUR LAST RIDE EXPLODED.

**18–23 seconds — TOBI:** I WILL FIND SOMETHING FASTER.

## 5B — The last dive · 14.5 seconds

**Presentation:** Three illustrated panels in a narrow cinematic strip, with gentle camera travel within each panel. This is not an enlarged gameplay scene.

**Heading:** BLACK MOON / THE LAST DIVE

**0–4 seconds — picture:** Establish the orbital threat and DHH’s approach. No dialogue.

**4–6.6 seconds — TOBI / RADIO:** TELL ME YOU HAVE A WAY BACK.

**6.6–9.6 seconds — DHH:** WORKING ON IT.

**Action across the panels:** DHH secures his tether, exits the spaceship, and prepares the captured weapon for the confrontation.

**9.6 seconds onward — DHH:** LET’S FINISH THIS.

**At 14.5 seconds:** Cut to player control: DHH outside the ship, tether attached, arc rifle ready.

## 5C — The enclosure · gameplay

**Level title:** 05 / BLACK MOON

**Boss title:** THE ENCLOSURE

**Picture:** Earth fills the background. Stars shimmer, a satellite passes, cloud storms flash at a distance, and Earth’s atmospheric edge glows. The shuttle remains nearby, tethered to DHH.

**Action:** DHH uses the arc rifle and thruster dash to survive the orbital bullet patterns while destroying the two containment nodes. The enclosing space figure holds the jellyfish-like intelligence.

**Dialogue:** None.

## 5D — The intelligence is released · gameplay transition

**Boss title:** THE INTELLIGENCE

**Action:** The enclosure breaks away. The intelligence is exposed, and enemy projectiles briefly clear for the transition.

**Picture:** The Earth/orbit background transitions over three seconds into the animated Omarchy terminal-text screensaver.

**Action:** The fight continues with curved pinwheels, aimed needles, and gapped curtains. There is no additional scenic effect layer on top of the screensaver.

**Dialogue:** None.

## 5E — Containment failure · final combat phase

**Boss title:** CONTAINMENT FAILURE

**Action:** The intelligence powers up again. Its patterns become faster and denser. DHH remains tethered and uses the stolen arc rifle to finish it.

**Dialogue:** None.

## 5F — Collapse and the way home · ending, 0–7 seconds

**Picture:** The final enemy destabilizes and collapses into a nova. The camera pulls back. Luminous fragments gather around a forming portal.

**Action:** DHH is drawn toward the portal. His tether detaches at approximately 3.1 seconds. He reaches toward the opening and disappears into it.

**Dialogue / titles:** None. The ending plays visually.

## 5G — Falling back to Earth · ending, 7–11 seconds

**Picture:** A wide sky shot establishes the height. A portal closes above DHH as he falls toward the coast.

**Action:** DHH tumbles downward. Vertical streaks emphasize the fall.

**Dialogue:** None.

## 5H — Tobi’s second catch · ending, 11–14.4 seconds

**Picture:** Cut closer to the coastal road. The car races into position beneath DHH.

**At approximately 13 seconds:** DHH lands in the moving car. The suspension compresses and rebounds; tire smoke trails behind it.

**Action:** Tobi drives on without stopping. The camera tracks the catch, then changes to a rear view.

**Dialogue:** None.

## 5I — Drive away · ending, 14.4–22 seconds

**Picture:** Rear view of the car carrying both men. Road markings rush beneath it as it recedes toward the skyline. The Omarchy wordmark appears above the destination.

**Final text:**

> OMACONTRA / THE END

**Prompt:** R / REPLAY · ESC / EXIT

---

# Appendix A — Failure and replay beats

These are alternate outcomes, not additional story scenes.

## Arcade continue screen — all levels

After the final-life death animation (1.2 seconds), cut to battered bust portraits of DHH and Tobi with their heads bowed.

**Heading:** CONTINUE?

**Countdown:** 10 through 1, one second per number.

**Prompt:** ENTER / SPACE / R — CONTINUE

**If accepted before timeout:** Both men lift their heads. A bright gleam crosses their eyes, accompanied by a comeback chime. The heading changes to BACK IN THE FIGHT, with LET’S GO. beneath. After 1.35 seconds, restart the current encounter with its normal full life allowance, skipping the introductory cutscene. Guardian retries stay at the guardians; other multi-phase bosses restart at the encounter’s first phase.

**If the timer expires:** A heavy finishing impact plays once. The portraits darken with a brief red flash.

**Heading:** GAME OVER

**Prompt:** ENTER / TITLE SCREEN · ESC / EXIT

The old retry labels described below belong to the underlying encounter’s death frame, before the new continue screen takes over.


- **On foot:** DHH reacts to a hit with a death-like tumble, then respawns with temporary protection while lives remain. Health ribbons disappear as lives are lost.
- **Quattro:** The car explodes on its final hit. The retry text reads `QUATTRO DOWN / R TO RETRY`.
- **Mist Gate:** Final defeat displays `DHH DOWN`, followed by `R / RETRY THE MIST GATE`.
- **Black Moon:** Final defeat displays `SIGNAL LOST`, followed by `R / RETRY     ESC / EXIT`.
- **Level progression:** Completing a level awards an extra health ribbon.
- **Unlimited lives:** The secret-code flag persists through the campaign. Hit reactions and recovery still occur.

# Appendix B — Older text still in source, not in the normal current story

These lines should not be mistaken for additional scenes when revising the main script.

## Unused journey opening and repeated ending cards

The original journey-beat tuple includes these, but the live sequence is sliced to start at the cellar and end at the wallpaper arrival:

> THE WORLD WATCHED THE FRONTIER LABS.
>
> THE REAL PROBLEM WAS IN A WINE CELLAR.

It also includes another “BUT IT DOESN'T MATTER / BECAUSE YOU CAN FIX ANYTHING” card and a cover-screen entry outside that live slice.

## Old separate guardian reveal

A legacy reveal renderer contains these lines, but the current wave defeat leads directly into the guardians on the same deck:

> THE SEA WAS ONLY A WALL
>
> THE DOCKYARD IS CHANGING
>
> DEAD ORBIT  /  BLACK COAT
>
> TOBI / RADIO: TWO OF THEM. WATCH BOTH SIDES.

# Appendix C — Where edits will be implemented

| Script section | Current source |
| --- | --- |
| Prologue, title timing, cellar dialogue, portal, wallpaper recognition | `story.py` |
| Prologue artwork, title screen, recognition timing and presentation | `art.py` |
| First-boss victory text | `battle_art.py` |
| Quattro reunion and rally outro | `chase_cinema.py` |
| Truck/robot finisher prompts | `chase_art.py`, `chase.py` |
| Harbor conversation and post-guardian radio | `journey_cinema.py` |
| Wave-to-guardian handoff and survivor close-up | `tide_guardians.py`, `tide_guardian_art.py`, `tide_art.py` |
| Dragon entrance, ultimate charge, Tobi crash dialogue | `foundry_art.py` |
| Dragon phase rules and rescue timing | `foundry.py` |
| Elevator, last-dive dialogue, ending visuals | `finale_art.py` |
| Final-level phase rules and cinematic durations | `finale.py` |
| Opening music and continuous playlist | `intro_music.py` |
| Scene progression and skip/continue behavior | `boss_app.py` |

## Revision notes

Add proposed changes here, or edit the relevant scene directly. Scene IDs such as **4E** and **5B** can be used to refer to changes without rewriting the whole document.
