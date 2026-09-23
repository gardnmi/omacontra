"""One explicit runtime inventory shared by local installs and release packages."""
from pathlib import Path, PurePosixPath
import shutil


def asset_paths(root):
    root = Path(root)
    result = []
    for line in (root / 'release-assets.txt').read_text().splitlines():
        name = line.strip()
        if not name or name.startswith('#'):
            continue
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or name in result:
            raise ValueError(f'Invalid or duplicate release asset: {name}')
        source = root / 'assets' / name
        if not source.is_file() or not source.resolve().is_relative_to((root / 'assets').resolve()):
            raise ValueError(f'Missing or unsafe release asset: {name}')
        result.append(name)
    if not result:
        raise ValueError('Release asset inventory is empty')
    return result


def stage_game(root, target):
    """Copy a complete playable tree without development assets or bytecode."""
    root, target = Path(root), Path(target)
    assets = asset_paths(root)  # Validate everything before writing.
    target.mkdir(parents=True, exist_ok=True)
    for name in ('main.py', 'README.md'):
        shutil.copy2(root / name, target / name)
    for name in ('LICENSE',):
        if (root/name).is_file():shutil.copy2(root/name,target/name)
    for name in ('SUPPORT.md','RELEASE_NOTES.md'):
        source=root/'docs'/name
        if source.is_file():
            (target/'docs').mkdir(exist_ok=True)
            shutil.copy2(source,target/'docs'/name)
    shutil.copytree(root / 'src', target / 'src',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    shutil.copytree(root / 'THIRD_PARTY', target / 'THIRD_PARTY')
    for name in assets:
        destination = target / 'assets' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / 'assets' / name, destination)
