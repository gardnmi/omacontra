# Shipped asset permissions inventory

This inventory records evidence in the repository. A source URL, download, or
generation prompt is provenance, not by itself a redistribution grant.
Items marked pending require the project owner's confirmation before release.
No third-party material is relicensed by the game's code license.

## Recorded third-party licenses

| Material | Author / source | Recorded terms and evidence |
| --- | --- | --- |
| Window helper | Hyprsplitter | MIT; `hyprsplitter-LICENSE.txt` |
| Screensaver effects | 37signals / omacom-io; ChrisBuilds | MIT; `assets/screensaver/LICENSE-ttfx` and README |
| Sci-Fi Sounds and Impact Sounds | Kenney | CC0; original License.txt files under `assets/audio/sources/kenney-*` |
| Firearm textures used in derived effects | Ben Jaszczak, Brian Nelson, Kevin Heras, Matthew Nanney | CC0; `assets/audio/sources/README.md` |
| Ocean Splash | Thimras | CC0; source and adaptations in `assets/audio/sources/README.md` |
| 6 Short Water Splashes | ezwa, submitted by qubodup | CC0; source and adaptations in the same notes |
| Short wind sound | remaxim | CC0; source and adaptations in the same notes |
| Thunder | Jerimee, using René Nyffenegger's cSound instrument | CC BY 3.0; source, license link, and modifications in the same notes |
| Force field electric hum | Hansjörg Malthaner (Varkalandar) | CC BY 4.0; `assets/audio/sources/force-field/LICENSE.md`, with author, source, license link, and modifications |

The detailed audio notes preserve links and descriptions of trimming, filtering,
resampling, mixing, and other adaptations. Their earlier tuning sections are
historical; later replacement sections describe the current assets. Original
recordings used only for rebuilding are excluded from the runtime download.

## Soundtrack: creation confirmed, redistribution confirmation pending

| Shipped song | Recorded source | Outstanding evidence |
| --- | --- | --- |
| Omacontra Opening Theme | Owner-supplied `konami-hero-lead [usesuno.com].mp3` | Owner confirmation of applicable generation/account and redistribution rights |
| Off Duty Mercenary | Owner-supplied Suno download | Same |
| Contra | Owner-supplied Suno download | Same |
| Boss Battle Protocol | Owner-supplied Suno download | Same |
| Arcade Armageddon | Owner-supplied Suno download | Same |
| Omarchy Oligarchy (Synthwave Mix) | YZL81 / Omarchy Radio | Rights-holder permission or applicable redistribution license |

On 2026-09-22 the project owner confirmed that Suno created the music. Account
ownership, applicable terms, and permission for the YZL81 recording were not
confirmed by that creation credit.

`assets/audio/library.json` records filenames, source URLs, authors where known,
and the conversion to 96 kbps target VBR Opus. Download availability is not recorded
here as permission. The five supplied songs do not yet have creator/account
ownership evidence recorded in this repository.

## Artwork and branding: confirmation pending

- The project owner credits Codex / OpenAI GPT-6 Astra (medium) for the
  AI-generated original code and artwork (2026-09-22).
- AI-assisted game sprites, backgrounds, cinematics, and box art: generation
  prompts and source notes are retained under `assets/` and `docs/`. Confirm the
  project's rights to distribute the outputs and the reference/source material.
- `assets/arrival-wallpaper.png`: HBG3 wallpaper from the Omarchy Harbordark
  theme. Record the original artist and applicable reuse terms or permission.
- Omarchy screensaver branding and wallpaper-derived material: the ttfx code's
  MIT license does not by itself establish terms for all bundled artwork/branding.
- DHH and Tobi are portrayed as fictional action-adventure characters. Do not
  represent the game as an official endorsement by its subjects or referenced brands.

## Completing this inventory

Record the confirming person, date, scope, and a stable license/permission reference
for each pending entry. Keep private correspondence outside the public repository;
record a non-sensitive summary or permission identifier here. Do not mark an item
cleared based only on its attribution or its presence in the game.
