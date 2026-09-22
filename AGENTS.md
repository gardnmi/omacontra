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
