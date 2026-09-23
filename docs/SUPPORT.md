# Support and known limitations

## Supported setup

Omarchy / Arch Linux with a running Hyprland session supporting the Lua API
(Hyprland 0.55 or newer). Other compositors, Windows, and macOS are not supported.
Keyboard and mouse only; controller support is not implemented.

The game renders at 1280 × 720 and scales to your display. Performance on lower-end
hardware is not yet benchmarked; no minimum GPU or guaranteed frame rate is claimed.
The finale screensaver animations and detailed boss scenes are useful stress tests.

## Updates

Re-run the README installer command to update a per-user install. Direct Arch
packages require installing a newer package with `sudo pacman -U`; GitHub downloads
are not an automatic pacman update source. Both preserve settings and records.

Check `omacontra --version` after an update. If it reports an older version, run
`type -a omacontra` to find duplicate launchers. A per-user install can take
precedence over `/usr/bin/omacontra`; see the package guide for switching methods.
Restart the game after updating. Developer stage selection and unlimited-lives
runs have separate record categories. Hardcore mode has no continues.

## Report a bug

Use [GitHub Issues](https://github.com/gardnmi/omacontra/issues/new/choose).
Include the game version, installation method, Hyprland version, stage/phase,
steps to reproduce, and a screenshot or short recording where helpful.
For frame-rate problems include CPU, GPU, display resolution, and the affected scene.

For startup problems, launch `omacontra` from a terminal and copy the error output.
`omacontra --smoke-test` opens the game for six seconds to check its window setup;
run this inside Hyprland. Review logs for personal information before posting.

Profiles are stored in `~/.config/omacontra/profile.json` (or under XDG_CONFIG_HOME).
Uninstalling preserves them. Back up that file before testing profile changes.

Automated tests cover simulation, rendering, and installation, but hosted CI does
not run the interactive Hyprland window test or replace a full human playthrough.
