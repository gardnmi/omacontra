# OMACONTRA

![Omacontra retro box cover: back, spine, and front, featuring DHH, Tobi, the dragon and scenes from the game](docs/images/omacontra-box-cover.png)

A Contra-inspired **boss-only** fullscreen game. Five encounters bring wallpaper worlds to life: the Reaper, Quattro Run, Tidebreaker, the Mist Gate, and Black Moon. DHH runs, jumps, ducks,
and fires a machine gun. Later encounters introduce an arc rifle and a spacesuit firing stream.

## Install on Omarchy

Install Omacontra as a standalone app on your Omarchy desktop. The installer
creates an **Omacontra** entry in the apps menu and an executable named
`omacontra`. All artwork, music, and screensaver animations are included. The game renders
at 720p internally by default and scales to your display, keeping detailed
scene rendering independent of monitor resolution.

### Quick install (when the repository is public)

Run this in your Omarchy terminal:

```sh
curl -fsSL https://raw.githubusercontent.com/gardnmi/omacontra/main/install.sh | bash
```

No Git checkout or AUR package is needed. The installer downloads a verified game
snapshot, installs missing system dependencies (asking for your password if
needed), and creates the **Omacontra** app-menu entry and `omacontra` executable.
Run it as your normal user, without `sudo`. Re-run the command to update to the
snapshot selected by the installer; settings and personal bests are preserved.

**The repository is currently private**, so this unauthenticated command is not
yet available to the public. Authorized testers can use the source installation
below. A downloadable Arch package is also prepared; see
[direct package builds and releases](packaging/arch/README.md). It can be hosted
on GitHub Releases and installed directly, without AUR.

### Install from source

### 1. Install the required packages

Open a terminal in Omarchy and run:

```sh
omarchy pkg add git python python-gobject python-cairo gtk3 mpv sdl2-compat
```

Omarchy installs any missing packages and may ask for your password.

### 2. Download and install the game

Clone the repository and run the installer:

```sh
git clone https://github.com/gardnmi/omacontra.git
cd omacontra
./install.py
```

> Before the public release, cloning requires a GitHub account with repository access.

Run the game installer as your normal user. It creates:

| Installed item | Location |
| --- | --- |
| Executable launcher | `~/.local/bin/omacontra` |
| Game and assets | `~/.local/share/omacontra/` |
| Apps-menu entry | `~/.local/share/applications/omacontra.desktop` |

### 3. Play

Open the **Omarchy apps menu**, search for **Omacontra**, and launch it.
You can also start the executable from any terminal:

```sh
omacontra
```

If your shell cannot find the command, run `~/.local/bin/omacontra` directly.
The installed game runs independently of the downloaded repository.

### Update

From your downloaded `omacontra` repository:

```sh
git pull --ff-only
./install.py
```

Updates preserve your settings and personal bests.

### Uninstall

From that same repository:

```sh
./install.py --uninstall
```

This removes the executable, game files, and apps-menu entry. Settings and records
remain in `~/.config/omacontra/profile.json` (or your `XDG_CONFIG_HOME` location).

### Troubleshooting

Run `./install.py --check` to check the required dependencies. Launch the game
inside your Omarchy desktop session. The current window host uses Hyprland's Lua
API; older Hyprland builds and other compositors are not supported yet.

## Development

To run directly from the source checkout without installing:

```sh
./omacontra
./omacontra --boss
./omacontra --level 4
```

Run the test suite and fullscreen launch check:

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
