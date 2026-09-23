#!/usr/bin/env python3
"""Build the small, reproducible runtime download (not a source-code archive)."""
import argparse
import gzip
import hashlib
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from release_assets import stage_game


def build(output):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='omacontra-release-') as temporary:
        game = Path(temporary) / 'omacontra'
        stage_game(ROOT, game)
        for name in ('install.py', 'release_assets.py', 'release-assets.txt'):
            shutil.copy2(ROOT / name, game / name)
        with output.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|') as archive:
                for path in [game, *sorted(game.rglob('*'))]:
                    info = archive.gettarinfo(str(path), str(path.relative_to(game.parent)))
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ''
                    info.mode = 0o755 if path.is_dir() else 0o644
                    if path.is_file():
                        with path.open('rb') as source:
                            archive.addfile(info, source)
                    else:
                        archive.addfile(info)
    with output.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    output.with_name(output.name + '.sha256').write_text(f'{checksum}  {output.name}\n')
    print(f'{output}: {output.stat().st_size / 1048576:.1f} MiB\nSHA256 {checksum}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/omacontra-runtime.tar.gz')
    args = parser.parse_args()
    build(args.output)
