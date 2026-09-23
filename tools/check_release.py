#!/usr/bin/env python3
"""Verify a built runtime download against the installer and package pins."""
import hashlib
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    root = Path(root)
    version = runpy.run_path(str(root/'src/omacontra/version.py'))['__version__']
    installer = (root/'install.sh').read_text()
    package = (root/'packaging/arch/PKGBUILD').read_text()
    with (root/'dist/omacontra-runtime.tar.gz').open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    for text, pattern in ((installer, r'local checksum=([a-f0-9]{64})'),
                          (package, r"sha256sums=\('([a-f0-9]{64})'")):
        match = re.search(pattern, text)
        if not match or match[1] != digest:
            raise ValueError('Archive checksum differs from installer/package; rebuild and update both pins.')
    for text, pattern in ((installer, r'local release=(\S+)'), (package, r'_release=(\S+)')):
        match = re.search(pattern, text)
        if not match or match[1] != 'v'+version:
            raise ValueError('Release tag must match the version displayed by the game.')
    sidecar = (root/'dist/omacontra-runtime.tar.gz.sha256').read_text().split()[0]
    if sidecar != digest:raise ValueError('Archive checksum sidecar is stale.')
    print(f'Release {version}: archive, installer, and package pins match.')


if __name__ == '__main__':
    check()
