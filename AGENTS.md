# Omacontra

This repository is the standalone game, extracted from Hyprsplitter.

- Run tests: python -m unittest discover -s . -p "test_*.py".
- Fullscreen smoke check in a Hyprland session: python main.py --smoke-test.
- Keep assets and existing source/provenance notes together.
- Review captures and generated videos stay local, outside Git.
- Installer: python install.py; copies runtime files and assets, not tests/reviews.
- Worktrees belong under ~/Worktrees/omacontra/<branch-slug>. Inspect registered worktrees before creating or removing them.
