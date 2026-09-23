"""Version identification works without a desktop or graphics packages."""
from pathlib import Path
import subprocess
import sys
import unittest
from omacontra.version import __version__

ROOT=Path(__file__).resolve().parents[1]

class VersionTests(unittest.TestCase):
    def test_version_from_unrelated_directory_without_site_packages(self):
        result=subprocess.run([sys.executable,'-S',str(ROOT/'main.py'),'--version'],
                              cwd='/tmp',capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'Omacontra '+__version__)
