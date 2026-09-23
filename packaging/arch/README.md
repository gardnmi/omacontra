# Omacontra Arch package

This directory contains a native Arch package recipe, executable launcher,
and desktop entry. Distribute the built package directly through GitHub Releases.
**No AUR listing is needed or planned.**
The source repository is currently private; builders need repository access.

The initial package is a pre-release snapshot, `0.1.0.r24.g40e9992`, pinned to
commit `40e99926b147aea0575d5f0d0c58d78a411baa2c`. The game source and both integration
files have SHA-256 checksums. Uncommitted changes and later commits are not
silently included. The package includes the fullscreen/tiling and 720p changes.

## Build and install now

From a checkout with access to the game's GitHub repository:

```sh
omarchy pkg add base-devel git
mkdir -p build/arch
cp packaging/arch/{PKGBUILD,omacontra.sh,omacontra.desktop} build/arch/
cd build/arch
makepkg --syncdeps
sudo pacman -U ./omacontra-*.pkg.tar.zst
```

Run `makepkg` as your normal user. Dependency installation and `pacman -U` may
request your password. The build downloads the pinned source, including assets;
it installs no development tools into the game itself. Later builds in the same
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

1. Choose a reviewed game commit or release tag. Update `_commit` and `pkgver` in
   `PKGBUILD`; reset `pkgrel=1` for a new upstream version. Increment `pkgrel` when
   only the package recipe changes.
2. Run `makepkg --geninteg` in this directory and replace `sha256sums` with its
   output. Regenerate `.SRCINFO` with `makepkg --printsrcinfo > .SRCINFO`.
3. Build and test the package, then attach the `.pkg.tar.zst` and its SHA-256
   checksum file to a GitHub Release. Players install it with `sudo pacman -U`
   and launch **Omacontra**. No AUR account or package submission is involved.
4. Keep the root `install.sh` snapshot in sync: update its commit and checksum
   using the exact GitHub API tarball URL in that script. Test both installation
   and replacement of an existing install. The direct installer uses the
   per-user layout; the native package uses `/usr`. These are alternative methods.
5. Make the repository/release public when ready. The existing
   `THIRD_PARTY/README.md` says no project-wide license has been assigned.
   `LicenseRef-Unknown` reports that status without assigning a new license;
   finalize distribution terms and preserve asset/music attribution for release.

A downloaded local package does not receive package-manager updates from GitHub
automatically. Download and install a newer release with `pacman -U` to update.
The per-user direct installer updates when the player re-runs it. Both preserve
the same settings and records.
