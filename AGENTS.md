# Omacontra

This repository is the standalone game, extracted from Hyprsplitter.

- Run tests: python tools/test.py.
- Fullscreen smoke check in a Hyprland session: python main.py --smoke-test.
- Keep assets and existing source/provenance notes together.
- Review captures and generated videos stay local, outside Git.
- Installer: python install.py; copies runtime files and assets, not tests/reviews.
- Worktrees belong under ~/Worktrees/omacontra/<branch-slug>. Inspect registered worktrees before creating or removing them.

## Structure

- Runtime lives in src/omacontra; use explicit package imports.
- Encounters live under stages/{reaper,highway,harbor,dragon,space}.
- Use omacontra.resources.ASSETS for assets, never paths relative to stage files.
- Developer tools belong in tools and tests belong in tests.
- Keep main.py and the omacontra launcher compatible with the installer.
- Check install, upgrade, and source-independent launch when changing layout.

## Art tools and workflow

The primary tool used to generate and edit this game's raster artwork was
**Codex's built-in OpenAI image-generation tool** (`image_gen` / `imagegen`).
This includes character sprites, bosses, scenery, props, cinematic panels, and
README box art. Codex / OpenAI GPT-6 Astra (medium) is the project's credited
coding and art-direction agent; do not infer a particular underlying image-model
version from that agent name. Follow the available `imagegen` skill when making
new bitmap artwork or editing an existing image.

Supporting tools:

- **Image inspection (`view_image`)**: inspect reference assets, generated images,
  and rendered gameplay captures before accepting changes.
- **Python + Cairo**: prepare generated assets for runtime use and render the game.
  For example, `tools/build_dock_cargo.py` crops transparent padding and resizes
  generated trolley sprites; it does not generate the painted artwork.
- **`tools/asset_review.py`**: render repeatable checks through the actual stage
  renderers. Run `python tools/asset_review.py --output review/art-check`.
- **FFmpeg**: encode animated review captures and inspect motion from gameplay
  recordings; it is a review/processing tool, not the image generator.

When changing art:

1. Use the existing game assets and supplied references to match the detailed
   pixel-art style, palette, lighting, proportions, and character identity.
2. Generate or edit through the image-generation tool. Inspect the output for
   anatomy, weapon grips, silhouette, transparency, and unwanted background halos.
3. Keep sprite anchors, frame coordinates, and collision geometry aligned when
   integrating the asset. Check it at actual gameplay scale, including in motion.
4. Preserve exact prompts, reference descriptions, output filenames, and source
   credits alongside assets. Local generated-image paths are provenance only;
   runtime code must never depend on them.
5. Add shipped assets to `release-assets.txt`. Keep review captures and large
   generation intermediates outside the release inventory. Preserve third-party
   notices; creation-tool credits do not establish redistribution permissions.

Recorded examples:

- `assets/character-prompts.json`: built-in image-generation edits and references.
- `assets/tide-dock-cargo-source.md`: exact trolley prompts and normalization steps.
- `docs/images/omacontra-box-cover.md`: cover-art references and generation prompt.
- `THIRD_PARTY/README.md`: creation credits and third-party attribution.

Suno is credited for music generation, not visual artwork.
