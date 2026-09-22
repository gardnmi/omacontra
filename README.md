# OMACONTRA

A Contra-inspired **boss-only** fullscreen game. Five encounters bring wallpaper worlds to life: the Reaper, Quattro Run, Tidebreaker, the Mist Gate, and Black Moon. DHH runs, jumps, ducks,
and fires a machine gun. Later encounters introduce an arc rifle and a spacesuit firing stream.

## Install and play

Standalone Linux/Hyprland game. It no longer needs the Hyprsplitter checkout or an
installed Omarchy theme; the game art, soundtrack, and screensaver frames ship here.
The current window host targets the Hyprland Lua API used by this Omarchy system.
Other compositors and older Hyprland builds are not yet supported.

Runtime dependencies: Python 3.11+, PyGObject with GTK 3 and Cairo integration,
PyCairo, mpv, and SDL2. On Omarchy/Arch:

```sh
sudo pacman -S --needed python python-gobject python-cairo gtk3 mpv sdl2-compat
```

Clone using an account with access to this private repository, then install:

```sh
git clone https://github.com/gardnmi/omacontra.git
cd omacontra
python install.py --check
python install.py
omacontra
```

The installer copies runtime code and assets to `~/.local/share/omacontra`, adds
`~/.local/bin/omacontra`, and creates an **Omacontra** application-menu entry.
If `~/.local/bin` is not on PATH, use that full launcher path. Installation does
not require root and does not modify the desktop's configuration. Re-run the
installer after pulling updates. `python install.py --uninstall` removes the app
but preserves settings and personal bests in `~/.config/omacontra/profile.json`
(or the corresponding XDG_CONFIG_HOME location). An alternate prefix is supported
with `--prefix /path/to/prefix` for both installation and removal.

Run directly from the checkout:

```sh
./omacontra
./omacontra --boss
./omacontra --level 4
```

## Development

```sh
python tools/test.py
./omacontra --smoke-test
```

Generated review captures stay locally in `review/` and are excluded from Git.
Asset provenance and source credits remain alongside assets and in `THIRD_PARTY/`.
Optional asset-rebuild tools may additionally need ffmpeg, Pillow or ttfx; these
are not needed to play the prebuilt game. The copied window helper retains its
original MIT notice; this move does not assign a new license to the game's art
or music.

## Project layout

- `src/omacontra/`: runtime package and application host.
- `src/omacontra/stages/`: Reaper, highway, harbor, dragon, and space encounters.
- `src/omacontra/rendering/`: shared sprites, poses, and visual effects.
- `src/omacontra/audio/`: soundtrack and sound-effect playback.
- `src/omacontra/ui/`: menus, story, cinematics, and continue screen.
- `tests/`: gameplay, rendering, audio, and installation regression tests.
- `tools/`: asset builders, visual reviews, and control-only playtest utilities.
- `assets/`: shipped artwork, audio, and pre-rendered screensaver frames.
- `docs/`: architecture, gameplay notes, audits, and the preserved original opening.

All runtime asset locations come from `src/omacontra/resources.py`. The installer
ships the runtime package and assets; development tools and tests stay in the repo.
`main.py` and `./omacontra` remain supported launchers.

See [architecture](docs/ARCHITECTURE.md), [gameplay/design notes](docs/GAMEPLAY.md),
and the [full game script](GAME_SCRIPT.md).
