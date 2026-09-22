#!/usr/bin/env python3
"""Run the game test suite without installing the package."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2 if '-v' in sys.argv else 1).run(suite)
    raise SystemExit(not result.wasSuccessful())
