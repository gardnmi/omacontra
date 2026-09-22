"""Installation boundaries and an independent launch after restructuring."""
from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import install as installer


class InstallTests(unittest.TestCase):
    def test_install_upgrade_launch_and_uninstall_from_unrelated_directory(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'checkout'
            source.mkdir()
            shutil.copytree(installer.ROOT / 'src', source / 'src', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(installer.ROOT / 'main.py', source / 'main.py')
            (source / 'README.md').write_text('Test installation')
            (source / 'assets').mkdir()
            (source / 'assets/sentinel').write_text('asset')
            (source / 'THIRD_PARTY').mkdir()
            (source / 'test_unused.py').write_text('must not ship')
            prefix = root / 'install with spaces'
            with patch.object(installer, 'ROOT', source), patch.object(installer, 'check_dependencies'), redirect_stdout(io.StringIO()):
                installer.install(prefix)
                target, launcher, desktop = installer.locations(prefix)
                self.assertFalse((target / 'test_unused.py').exists())
                self.assertFalse(list(target.rglob('__pycache__')))
                self.assertTrue((target / 'assets/sentinel').exists())
                env = dict(os.environ)
                env.pop('PYTHONPATH', None)
                result = subprocess.run([str(launcher), '--help'], cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('--guardians', result.stdout)
                result = subprocess.run([sys.executable, '-c', 'import sys; sys.path.insert(0, sys.argv[1]); from omacontra.resources import ASSETS; print(ASSETS)', str(target / 'src')], cwd=root, env=env, capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), str(target / 'assets'))
                (target / 'stale-module.py').write_text('old install')
                installer.install(prefix)
                self.assertFalse((target / 'stale-module.py').exists())
                profile = prefix / 'config/omacontra/profile.json'
                profile.parent.mkdir(parents=True)
                profile.write_text('keep my records')
                installer.uninstall(prefix)
                self.assertFalse(target.exists() or launcher.exists() or desktop.exists())
                self.assertEqual(profile.read_text(), 'keep my records')

    def test_unmanaged_directory_is_never_replaced_or_removed(self):
        with TemporaryDirectory() as temp:
            prefix = Path(temp)
            target, _, _ = installer.locations(prefix)
            target.mkdir(parents=True)
            protected = target / 'keep.txt'
            protected.write_text('user data')
            with patch.object(installer, 'check_dependencies'):
                with self.assertRaises(RuntimeError):
                    installer.install(prefix)
            with self.assertRaises(RuntimeError):
                installer.uninstall(prefix)
            self.assertEqual(protected.read_text(), 'user data')
