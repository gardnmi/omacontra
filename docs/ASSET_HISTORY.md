# Asset history from Hyprsplitter

Archived at extraction; includes context for other prototypes. Omacontra assets referenced below now live in this repository.

# Asset provenance

Project code is covered by the [MIT License](../LICENSE). This inventory
documents what is present; that license does not grant rights to third-party
artwork or trademarks.

| Asset | Current provenance / release status |
| --- | --- |
| `docs/omatari-console.png` | Still rendered from the project’s Cairo console and cartridge artwork; used as the README header. |
| `docs/gameplay.gif` | Existing repository gameplay recording; confirm author and permission to redistribute. |
| `experiments/platform-lab/assets/omarchy.png` | Omarchy wordmark bitmap used by rally/platform artwork; upstream source and redistribution terms need confirmation. |
| `experiments/lemur-falls/assets/omacon-2026.png` | User-supplied OMACON 2026 event artwork; source and redistribution permission need confirmation before release. |
| `assets/omacontra-cover.png`, `cover-v1.png` | Generated from user-supplied Contra, DHH, Tobi, and skull references; fictional game artwork. Third-party references are not licensed by the code license. |
| `assets/dhh-sprites.png`, `dhh-body.png`, `dhh-weapon.png`, `reaper-sprites.png`, `reaper-arena.png`, `intro-cellar.png` | AI-generated pixel-art atlases and stage. Reaper design derives from the user's installed HarborDark `HBG3.png`; upstream wallpaper creator/redistribution terms remain unconfirmed. Magenta is decoded as transparency at runtime. |
| Installed HarborDark `backgrounds/HBG3.png` | Read locally for the wallpaper-to-boss transition; original file not bundled or modified. |
| Installed `/usr/share/omarchy/logo.txt` | Read at runtime from the user's Omarchy installation; not copied into this repository by setup. |
| Installed fonts / theme palette | Read/rendered through the user's installation; not bundled. |
| Python/Cairo drawings | Artwork defined in repository source, including parody logos, console, vehicles, and characters. Code licensing does not grant third-party trademark rights. |

Omatari is an independent project. Names and visual references to Omarchy,
OMACON, Atari, Audi, Apple, Microsoft, and Linux/Tux do not imply affiliation
or endorsement.

For every newly contributed asset, include the original URL or source, creator,
license text or license URL, attribution requirements, and modifications.
Do not describe assets with unknown provenance as covered by the project's code
license. Replace or obtain permission for unresolved assets before packaging
them in a public release.

The Quattro level bundles `assets/quattro-road.png`, `quattro-car.png`, and `quattro-enemies.png`, generated with the built-in image generation tool from the user-provided rally wallpaper and the existing pixel-art sprites. The original wallpaper is not bundled. Vehicle sheets preserve their alpha channel, including sunset colors. Prompts and reference paths are recorded in `assets/quattro-prompts.json`. Brand marks and third-party reference designs are not claims of original ownership.

`assets/quattro-munitions.png` contains generated industrial tire-shredder and rocket sprites, matching the Quattro enemy sheet. Generated with the built-in image tool; prompt recorded in the Quattro prompt manifest.

`quattro-coast.png` and `quattro-guardrail.png` are generated derivatives of the existing Quattro road artwork: a background without the rail/road paint, plus an isolated transparent rail. They replace the old rectangular background-strip scrolling. Both live in `assets/`; prompts are in `quattro-rail-prompts.json`.

`quattro-bazooka.png` is an isolated generated launcher matching the existing DHH weapon art, used for the rooftop finisher. Its prompt is recorded in `assets/quattro-bazooka-prompt.json`.

`quattro-rally-cinema.png` is a generated two-layer ending atlas: sunset dirt-crest scenery above, transparent front three-quarter airborne Quattro below. Generated with the built-in image tool using the supplied wallpaper for composition and the existing car for style. Prompt: `assets/quattro-rally-prompt.json`.

`quattro-explosion.png` is a generated six-frame pixel-art fuel detonation and smoke atlas, replacing the repeated impact starbursts. Built-in image tool prompt: `assets/quattro-explosion-prompt.json`.

`assets/tidebreaker-arena.png`, `tidebreaker-attacks.png`, `tidebreaker-calm.png`, and `journey-cinema.png` are generated pixel-art assets made with the built-in image tool. The ocean uses the Great Wave concept and existing Reaper art as style reference; the fictional cellar/harbor scenes use existing cellar and Quattro art for continuity. Attack sprites retain generated alpha. Exact prompts and reference filenames are in `assets/tidebreaker-prompts.json`. No original installed wallpaper was copied into the repository for Tidebreaker.

`assets/tidebreaker-guardians.png` and `tidebreaker-worlds.png` were generated with the built-in image tool using the user's two supplied wallpaper screenshots (black-coated hooded gunman and skeletal astronaut) and the existing Tidebreaker art. The source screenshots are not bundled. Guardian sprites retain generated transparency; environments translate the references' palettes into the game's pixel-art style. Exact prompts/reference descriptions: `assets/tidebreaker-guardians-prompts.json`. The source character designs remain third-party references with unconfirmed attribution/redistribution terms.

### Tidebreaker natural water attacks

`assets/tidebreaker-natural-waves.png` was generated with
the built-in image-generation tool on 2026-09-20, using the existing generated
water atlas as a style reference. Six natural swell/breaker/collapse frames
replace the claw and arm treatment. Original transparency is preserved; art
direction is recorded in `assets/tidebreaker-natural-waves-prompts.json` beside
the atlas.

`assets/tidebreaker-harpoon.png` was generated on
2026-09-20 with the built-in image-generation tool, referencing the existing
ship arena. It replaces the geometric placeholder with a detailed industrial
launcher. Art direction and runtime crop are recorded in
`assets/tidebreaker-harpoon-prompts.json` beside the prop.

### Foundry and Quattro rescue

The generated `foundry-arena.png`, `foundry-warden.png`, and
`foundry-rescue.png` in `assets/` were created with the
built-in image-generation tool on 2026-09-20. The arena references the locally
installed `ristretto/backgrounds/3-industrial-moon.jpg`; that original file is
not bundled. The rescue atlas references the game's existing generated
Quattro artwork. The Warden is a new furnace-machine design. Sprite alpha is
preserved, and source directions/cropping notes live in `foundry-prompts.json`.
The rescue is fictional game storytelling.

### Inferno Warden revision

`assets/foundry-inferno.png` was generated with the
built-in image-generation tool on 2026-09-20 using the user's supplied
black/olive horned-mech wallpaper attachment as reference. The sprite replaces
the boiler guardian in gameplay and the rescue. Original alpha is retained.
Reference and prompt are recorded in `foundry-inferno-prompt.json` beside it.

### Black Moon finale

`finale-atlas.png` and `finale-homecoming.png` in the boss-rush assets directory
were generated with the built-in image tool on 2026-09-20. The user's shuttle
and astronaut/jellyfish wallpapers informed the new sprite designs; the local
Nord black-moon wallpaper informed the code-drawn orbital backdrop. The atlas
received a second generation pass to remove its background and preserve alpha.
The homecoming is an original pixel-art coastal highway. Characters and rescue
are fictional game storytelling.

Finale polish: `finale-guardian.png` provides three astronaut poses and three
jellyfish poses closely referencing the supplied wallpaper; `finale-orbit.png`
is a new pixel-art adaptation of the Nord black-moon reference. The driver in
`finale-atlas.png` now matches the Foundry/Quattro Tobi design. Built-in
image generation was used, with prompts recorded in `assets/finale-prompts.json`.

`dhh-space-walk.png` adds a six-frame boarding animation, generated from the
existing DHH spacesuit reference with built-in image generation. Prompt and
transparency cleanup are recorded in `assets/finale-prompts.json`.

`dhh-portal-reach.png` is a built-in-generated, transparent cinematic pose for
the feet-first portal pull, matching the established spacesuit. Its prompt is
recorded in `assets/finale-prompts.json`.
