#!/usr/bin/env python3
"""Install or remove Omacontra for the current user; no root access required."""
import argparse
import importlib
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
from ctypes.util import find_library
from release_assets import stage_game

ROOT = Path(__file__).resolve().parent
MARKER = '.omacontra-install'


def check_dependencies():
    missing = []
    for module in ('gi', 'cairo'):
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    if 'gi' not in missing:
        import gi
        try:
            gi.require_version('Gtk', '3.0')
            gi.require_version('GLibUnix', '2.0')
            gi.require_foreign('cairo')
        except (ValueError, ImportError):
            missing.append('GTK 3 / GI Cairo integration')
    if not shutil.which('mpv'):
        missing.append('mpv')
    if not (find_library('SDL2') or find_library('SDL2-2.0')):
        missing.append('SDL2')
    if missing:
        raise RuntimeError('Missing dependencies: '+', '.join(missing)+
                           f'. Python: {sys.executable}. On Omarchy, install python-gobject, python-cairo, gtk3, mpv and sdl2-compat with pacman. See README.md.')


def locations(prefix):
    return prefix/'share/omacontra', prefix/'bin/omacontra', prefix/'share/applications/omacontra.desktop'


def install(prefix):
    check_dependencies()
    target, launcher, desktop = locations(prefix)
    if target == ROOT or ROOT.is_relative_to(target) or target.is_relative_to(ROOT):
        raise RuntimeError('Install outside the source checkout.')
    if target.exists() and not (target/MARKER).is_file():
        raise RuntimeError(f'Refusing to replace an unmanaged directory: {target}')
    for path in (launcher, desktop):
        if path.exists() and 'Managed by Omacontra' not in path.read_text():
            raise RuntimeError(f'Refusing to replace an unmanaged file: {path}')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.omacontra-', dir=target.parent) as temp:
        staged = Path(temp)/'game'
        staged.mkdir()
        stage_game(ROOT, staged)
        (staged/MARKER).write_text('Managed by Omacontra\n')
        backup = Path(temp)/'previous'
        if target.exists():
            target.rename(backup)
        try:
            staged.rename(target)
        except OSError:
            if backup.exists():
                backup.rename(target)
            raise
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text('#!/bin/sh\n# Managed by Omacontra\nexec '+shlex.quote(sys.executable)+' -E -s '+shlex.quote(str(target/'main.py'))+' "$@"\n')
    launcher.chmod(0o755)
    desktop.parent.mkdir(parents=True, exist_ok=True)
    command = str(launcher).replace('%', '%%').replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    command = command.replace('\\', '\\\\')  # Exec is also a string value: escape the quoting backslashes again.
    desktop.write_text('[Desktop Entry]\n# Managed by Omacontra\nType=Application\nName=Omacontra\nComment=Five worlds. One boss rush.\nExec="'+command+'"\nIcon='+str(target/'assets/omacontra-cover-v2.png')+'\nTerminal=false\nCategories=Game;ActionGame;\nStartupNotify=false\n')
    print(f'Installed {target}\nLaunch: {launcher}\nAlso available in your application menu as Omacontra.')


def uninstall(prefix):
    target, launcher, desktop = locations(prefix)
    if target.exists():
        if not (target/MARKER).is_file():
            raise RuntimeError(f'Refusing to remove an unmanaged directory: {target}')
        shutil.rmtree(target)
    for path in (launcher, desktop):
        if path.exists() and 'Managed by Omacontra' in path.read_text():
            path.unlink()
    print('Omacontra uninstalled. Settings and personal bests have been preserved.')


def main():
    # Arch packages install GI/Cairo for system Python, not mise/pyenv/venvs.
    system_python=Path('/usr/bin/python')
    if Path('/etc/arch-release').exists() and system_python.is_file():
        if (Path(sys.executable).resolve()!=system_python.resolve()
                or sys.prefix!=sys.base_prefix
                or not sys.flags.ignore_environment or not sys.flags.no_user_site):
            os.execv(str(system_python),[str(system_python),'-E','-s',str(ROOT/'install.py'),*sys.argv[1:]])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=Path.home()/'.local')
    parser.add_argument('--uninstall', action='store_true')
    parser.add_argument('--check', action='store_true', help='Check runtime dependencies without installing')
    args = parser.parse_args()
    try:
        if args.check:
            check_dependencies()
            print('Runtime dependencies available.')
        elif args.uninstall:
            uninstall(args.prefix.expanduser().resolve())
        else:
            install(args.prefix.expanduser().resolve())
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
