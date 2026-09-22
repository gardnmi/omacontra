#!/usr/bin/env python3
"""Compatibility launcher for the source checkout and installed app."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from omacontra.cli import main

if __name__ == "__main__":
    main()
