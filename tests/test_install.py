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
            shutil.copy2(installer.ROOT/'LICENSE',source/'LICENSE')
            (source / 'docs').mkdir()
            for name in ('SUPPORT.md','RELEASE_NOTES.md'):
                shutil.copy2(installer.ROOT/'docs'/name,source/'docs'/name)
            (source / 'assets').mkdir()
            (source / 'assets/sentinel').write_text('asset')
            (source / 'release-assets.txt').write_text('sentinel\n')
            (source / 'assets/unused-original.wav').write_bytes(b'development only')
            (source / 'THIRD_PARTY').mkdir()
            (source / 'test_unused.py').write_text('must not ship')
            prefix = root / 'install with spaces'
            with patch.object(installer, 'ROOT', source), patch.object(installer, 'check_dependencies'), redirect_stdout(io.StringIO()):
                installer.install(prefix)
                target, launcher, desktop = installer.locations(prefix)
                self.assertEqual((target/'LICENSE').read_text(),(source/'LICENSE').read_text())
                self.assertTrue((target/'docs/SUPPORT.md').is_file())
                self.assertTrue((target/'docs/RELEASE_NOTES.md').is_file())
                self.assertFalse((target / 'test_unused.py').exists())
                self.assertFalse(list(target.rglob('__pycache__')))
                self.assertTrue((target / 'assets/sentinel').exists())
                self.assertFalse((target / 'assets/unused-original.wav').exists())
                env = dict(os.environ)
                env['PYTHONPATH'] = str(root/'unrelated-python-libraries')
                env['PYTHONHOME'] = str(root/'nonexistent-python-home')
                result = subprocess.run([str(launcher), '--help'], cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('--guardians', result.stdout)
                result = subprocess.run([sys.executable, '-E', '-s', '-c', 'import sys; sys.path.insert(0, sys.argv[1]); from omacontra.resources import ASSETS; print(ASSETS)', str(target / 'src')], cwd=root, env=env, capture_output=True, text=True, check=True)
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

    @unittest.skipUnless(Path('/etc/arch-release').exists(), 'Arch system-Python bootstrap')
    def test_source_installer_reexecutes_system_python_from_virtual_environment(self):
        with TemporaryDirectory() as temp:
            venv=Path(temp)/'venv'
            subprocess.run([sys.executable,'-m','venv','--without-pip',str(venv)],check=True)
            result=subprocess.run([str(venv/'bin/python'),str(installer.ROOT/'install.py'),'--check'],
                                  capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Runtime dependencies available',result.stdout)
