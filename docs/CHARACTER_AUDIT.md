# Character consistency audit — 2026-09-20

## Canonical reference

`assets/reference/canonical-characters.png` is the user-supplied title-screen reference. The title-screen cover itself is unchanged.

- **Tobi:** bald, clean-shaven, blue eyes, lean face; navy blue racing suit with lime piping and sponsor patches. No sunglasses or dark beard.
- **DHH:** shoulder-length brown hair, short salt-and-pepper beard, blue eyes, black sleeveless skull shirt and muscular build. White/graphite spacesuit when in orbit; face remains recognizable inside the visor.

## Active character coverage

| Where | Runtime artwork | Outcome |
| --- | --- | --- |
| Title | omacontra-cover.png | Original canonical artwork retained |
| Reaper, Tidebreaker, Foundry gameplay and Quattro gunner | dhh-body-canonical.png | Eight poses corrected; shared weapon arms retained |
| Cellar demonstration, portal incident, harbor | journey-cinema-canonical.png | Tobi corrected across all three panels; DHH retained with beard/hair |
| Quattro gameplay and intro | quattro-car-canonical.png | Driver corrected; DHH drawn from shared gameplay atlas |
| Quattro victory jump | quattro-rally-cinema-canonical.png | Both occupants corrected |
| Foundry rescue and docked Tobi | foundry-rescue-canonical.png | Driver, airborne, landing and standing Tobi corrected |
| Foundry car after ejection | foundry-rescue-empty.png | Empty cockpit retained; its unused character cells are never drawn |
| Shuttle boarding | dhh-space-walk-canonical.png | All six visor faces corrected |
| Space combat | dhh-space-rear.png | Rear-facing suit retained; no visible face |
| Portal pull | dhh-portal-reach-canonical.png | Visor face matched to title artwork |
| Falling DHH and front spacesuit | finale-people-canonical.png | Corrected human cells; original nonhuman atlas still supplies shuttle/boss |
| Lamborghini catch | finale-catch-car-canonical.png | Both occupants corrected; magenta-key background removes brown haze |
| Rear driving payoff | finale-car-rear-canonical.png | Tobi blue suit; DHH brown hair/black shirt |

`character_assets.py` routes shared logical sprite names to their approved replacements. Original alpha mattes are applied at load time for unchanged silhouettes, preventing generated background halos from entering scenes. The catch sheet uses chroma-key decoding and explicit frame/wheel coordinates.

Legacy `cover-v1.png`, `dhh-sprites.png`, `finale-catch-car.png`, `finale-catch-car-v2.png`, and `finale-catch-close.png` remain historical assets, not live character sources. Original human cells in `finale-atlas.png` are superseded at render time. Background, enemy, weapon, and effect sheets do not portray Tobi/DHH and were not redesigned.

## Opening recovered, not re-created

Exact original opening source was recovered from the local Codex session history and saved under `docs/original-opening/`. `story.py` restores its seven beats and durations. `art.py` restores its original `wine_cellar` and `story_card` methods. The later portal story still starts only after Enter at the title screen.

The cellar has blinking LEDs, spinning fan spokes, rising red illumination and a slow camera push. Review video: `review/opening-restored.mp4`.

## Review and provenance

Image edits used built-in image_gen; prompts and saved asset paths are recorded in `assets/character-prompts.json`. Earlier assets remain available for comparison.

```sh
python main.py --cutscene opening
python main.py --cutscene ending --at 12.4
python main.py --cutscene quattro-intro --at 1
```

Validation: offscreen rendering of actual game scenes, original-opening frame comparison, transparency checks, and the game unit/regression suite. This is not a claim of a manual full-game playthrough.
