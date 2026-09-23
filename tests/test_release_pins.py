"""Catch stale download checksums and mismatched release identities."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from tools.check_release import check

class ReleasePinTests(unittest.TestCase):
    def fixture(self,root):
        for name in ('src/omacontra','packaging/arch','dist'):(root/name).mkdir(parents=True)
        (root/'src/omacontra/version.py').write_text('__version__="1.0.0"\n')
        archive=root/'dist/omacontra-runtime.tar.gz';archive.write_bytes(b'test release')
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        (root/'install.sh').write_text(f'local release=v1.0.0\nlocal checksum={digest}\n')
        (root/'packaging/arch/PKGBUILD').write_text(f"_release=v1.0.0\nsha256sums=('{digest}')\n")
        (root/'dist/omacontra-runtime.tar.gz.sha256').write_text(digest+'  omacontra-runtime.tar.gz\n')

    def test_valid_release_and_tampered_archive(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root);check(root)
            (root/'dist/omacontra-runtime.tar.gz').write_bytes(b'wrong release')
            with self.assertRaisesRegex(ValueError,'checksum'):check(root)

    def test_stale_game_version_is_rejected(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            (root/'src/omacontra/version.py').write_text('__version__="2.0.0"\n')
            with self.assertRaisesRegex(ValueError,'tag'):check(root)
