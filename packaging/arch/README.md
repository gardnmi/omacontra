# Omacontra Arch package

This directory contains a native Arch package recipe, executable launcher,
and desktop entry. Distribute the built package directly through GitHub Releases.
**No AUR listing is needed or planned.**
The source repository is currently private; builders need repository access.

The lean download is built with `python tools/build_release.py`. The builder and
per-user installer share `release_assets.py` and `release-assets.txt` with this
package, so all three ship the same audited artwork, sound banks, and credits.
Original sound recordings and build intermediates remain development-only;
retired artwork has been removed from the current repository tree. All active
music, artwork, sound effects, and screensaver animation frames are unchanged.

## Build and install now

From a checkout with access to the game's GitHub repository:

```sh
omarchy pkg add base-devel python
python tools/build_release.py
mkdir -p build/arch-lean
cp packaging/arch/{PKGBUILD,omacontra.sh,omacontra.desktop} build/arch-lean/
cp dist/omacontra-runtime.tar.gz build/arch-lean/
cd build/arch-lean
makepkg --syncdeps
sudo pacman -U ./omacontra-*.pkg.tar.zst
```

Run `makepkg` as your normal user. Dependency installation and `pacman -U` may
request your password. The build uses the locally prepared runtime archive; after publication it can
also download that same archive from GitHub Releases. Its checksum must match
the recipe. It installs no development tools into the game itself. Later builds in the same
directory can use `makepkg --syncdeps --cleanbuild --force`.

The resulting `.pkg.tar.zst` is a normal Arch package. A release can distribute
this file directly for installation with `sudo pacman -U <downloaded-package>`;
users would not need to clone or build the game. Do not publish the package until
the source and distribution terms are ready for release.

### Switching from the existing per-user install

First install the package successfully. Then, from the source checkout, run:

```sh
./install.py --uninstall
hash -r
```

This removes the old `~/.local/bin/omacontra` and local desktop entry, which would
otherwise take precedence over the package. It preserves settings and personal
bests in `~/.config/omacontra/profile.json` (or `XDG_CONFIG_HOME`). The package uses
the same profile location. No uninstall hook deletes player data.

Launch **Omacontra** from the apps menu or run `/usr/bin/omacontra`. Remove the
package with `sudo pacman -R omacontra`.

## Installed layout

- `/usr/bin/omacontra`: executable launcher; forwards all command-line options.
- `/usr/share/omacontra/`: Python runtime, artwork, music, and attribution files.
- `/usr/share/applications/omacontra.desktop`: app-menu entry.
- `/usr/share/pixmaps/omacontra.png`: app icon.
- `/usr/share/licenses/omacontra/`: existing licensing/attribution notices.

The layout preserves the existing asset resolver. Tests, Git history, review
captures, and asset-generation tools do not ship. No system Python modules are
replaced, and no `pip` installation is required. Package-managed files are
read-only to normal users; settings remain in the user's config directory.

Dependencies: Python, PyGObject, Pycairo, GTK 3, mpv, SDL2 compatibility library,
and Hyprland >= 0.55 (Lua API). A compatible running desktop session is still
required. `arch=('any')` describes the architecture-independent Python/data
payload, not a promise that every architecture has been playtested.

## Validate

```sh
cd packaging/arch
bash -n PKGBUILD omacontra.sh
desktop-file-validate omacontra.desktop
makepkg --printsrcinfo > .SRCINFO
```

After building, inspect with `pacman -Qip <package>` and `pacman -Qlp <package>`.
After installing, run `/usr/bin/omacontra --help` from an unrelated directory and
`/usr/bin/omacontra --smoke-test` in Hyprland.

## Updating and publishing direct downloads

1. Run `python tools/build_release.py` from the project root. This creates
   `dist/omacontra-runtime.tar.gz` and its `.sha256` file. The archive includes the
   local installer and its inventory, not tests, build tools, or unused assets.
2. Set a new release tag in `_release` (PKGBUILD) and `release` (root `install.sh`).
   Update the archive checksum in both files from the builder's output. Keep the
   matching script beside the archive when sharing a private test download.
3. Update `pkgver`/`pkgrel`; regenerate `.SRCINFO` with
   `makepkg --printsrcinfo > .SRCINFO`. Build and test the package from the local
   archive as above. Copy the resulting `.pkg.tar.zst` to `dist/`.
4. Attach the runtime archive, its checksum, matching `install.sh`, native package,
   and package checksum to the selected GitHub Release when ready. Do not
   substitute GitHub's automatic full-source archive: that includes development
   data. No AUR listing or submission is needed.
5. Make the release public before advertising the online installer command.
   Preserve the project's existing licensing and asset/music attribution.

The current recipe targets `v0.1.0-lean.5`; it has not been published. For private
other-PC tests, transfer the native package directly, or transfer the runtime
archive plus `install.sh` and run `bash install.sh --archive ./omacontra-runtime.tar.gz`.

Downloaded local packages do not receive package-manager updates from GitHub
automatically. Install newer packages with `pacman -U`; per-user installations
update by re-running the matching direct installer. Both preserve player records.
