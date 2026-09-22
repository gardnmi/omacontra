# Code structure

## Entry points and installation

`./omacontra` runs `main.py`, which puts `src/` on the import path and calls
`omacontra.cli.main`. The CLI supports normal play, direct stage starts, cinematic
review, and preview rendering. The installer keeps this same layout, so launch
does not depend on the current directory or a source checkout.

`omacontra.resources` owns the data root. Shared artwork remains in `assets/`;
stage modules never calculate their own paths to assets. `install.py` copies the
runtime package, launcher, assets, and notices. It excludes caches and developer
tools. Preferences remain in the user's configuration directory across upgrades.

## Runtime responsibilities

- `boss_app`: window lifetime, input dispatch, simulation ticks, and stage routing.
- `desktop`: local Hyprland integration; no dependency on Hyprsplitter.
- `campaign_progress`, `hit_recovery`, `input_state`: shared gameplay state helpers.
- `stages/reaper`: original encounter and the shared Fight base used by later stages.
- `stages/highway`: Quattro physics, truck/robot encounter, highway scenery and cinematics.
- `stages/harbor`: moving deck, wave, guardian duo, cargo and harbor cinematics.
- `stages/dragon`: dragon, rotating laser, platforms, rising storm and rescue.
- `stages/space`: orbital combat, screensaver phase and ending.
- `rendering`: sprite decoding, character poses, shared effects and frame buffers.
- `audio`: recorded effects, soundtrack playback and stage sound banks.
- `ui`: introduction, menus, records, ribbon awards and continue portraits.

Stage art uses shared renderers and sometimes another stage's art for cinematic
continuity. Stage simulation still inherits the existing Reaper Fight base where
appropriate; this cleanup preserves that behavior rather than introducing a new
gameplay framework. Rendering must not advance simulation or alter hitboxes.

## Development tools

Run `python tools/test.py` from the repository (or by absolute path from elsewhere).
For an individual test, use `PYTHONPATH=src python -m unittest tests.test_foundry`.

- `tools/asset_review.py`: deterministic stage captures and optional video.
- `tools/chase_playtest.py`, `tools/foundry_playtest.py`: control-only simulations.
- `tools/build_*`: optional audio/screensaver asset rebuilds.
- `tools/render_wyrm_preview.py`: dragon cinematic/attack preview.

Tools may use development dependencies; none are imported by the installed game.
`docs/original-opening/` is explicitly an archival source copy, retained for
reference and excluded from installation. Asset generations and provenance are
preserved even when a superseded rendering function is removed.

## Cleanup verification

The package move is covered by the full gameplay/audio/rendering suite and install
tests (fresh install, upgrade, alternate paths, launch, uninstall, ownership guards).
Fixed frames from all five stages are also compared before and after the move to
catch visual changes caused by import or asset-path mistakes.
