#!/usr/bin/env bash
# Direct Omarchy installer. No Git checkout or AUR account required.
set -euo pipefail

main() {
    local archive='' action=install
    local -a installer_args=()
    while (($#)); do
        case "$1" in
            --archive)
                [[ $# -ge 2 ]] || { echo 'Missing --archive path.' >&2; return 1; }
                archive=$2; shift 2 ;;
            --prefix)
                [[ $# -ge 2 ]] || { echo 'Missing --prefix path.' >&2; return 1; }
                installer_args+=(--prefix "$2"); shift 2 ;;
            --uninstall) action=uninstall; installer_args+=(--uninstall); shift ;;
            --help|-h)
                echo 'Usage: bash install.sh [--prefix PATH] [--archive FILE] [--uninstall]'
                echo 'Installs Omacontra for the current user on Omarchy/Arch.'
                echo 'Re-run to update. Settings and personal bests are preserved.'
                return 0 ;;
            *) echo "Unknown option: $1" >&2; return 1 ;;
        esac
    done
    if ((EUID == 0)); then
        echo 'Run as your normal user, without sudo. Only missing system packages need sudo.' >&2
        return 1
    fi
    if [[ ! -f /etc/arch-release ]] || ! command -v pacman >/dev/null; then
        echo 'This installer supports Omarchy/Arch Linux.' >&2
        return 1
    fi
    local work
    work=$(mktemp -d -t omacontra-install.XXXXXXXX)
    # Expand the trusted mktemp path now; cleanup also runs on failed downloads.
    trap "rm -rf -- '$work'" EXIT
    local commit=40e99926b147aea0575d5f0d0c58d78a411baa2c
    local checksum=a9c1868251401d3a500d258863246aade21f812bcf0b824b419355a3588693d6
    if [[ -n $archive ]]; then
        cp -- "$archive" "$work/game.tar.gz"
    else
        command -v curl >/dev/null || { echo 'Install curl first.' >&2; return 1; }
        echo 'Downloading Omacontra (approximately 274 MB)...'
        if ! curl --fail --location --show-error --retry 3 --proto '=https' --tlsv1.2 \
            "https://api.github.com/repos/gardnmi/omacontra/tarball/$commit" -o "$work/game.tar.gz"; then
            echo 'Download failed. The repository must be public for this installer; authorized testers can use --archive FILE.' >&2
            return 1
        fi
    fi
    printf '%s  %s\n' "$checksum" "$work/game.tar.gz" | sha256sum --check --status || {
        echo 'Download verification failed; nothing has been installed.' >&2
        return 1
    }
    mkdir "$work/game"
    tar -xzf "$work/game.tar.gz" -C "$work/game" --strip-components=1 --no-same-owner --no-same-permissions
    local -a required=(python)
    if [[ $action == install ]]; then
        required+=(python-gobject python-cairo gtk3 mpv sdl2-compat 'hyprland>=0.55')
    fi
    local missing status=0
    missing=$(pacman -T "${required[@]}") || status=$?
    if ((status != 0 && status != 127)); then
        echo 'Unable to check installed packages.' >&2
        return 1
    fi
    if [[ -n $missing ]]; then
        if [[ ! -t 2 ]] || ! command -v sudo >/dev/null; then
            echo "Install these dependencies in a terminal, then retry: $missing" >&2
            return 1
        fi
        echo 'Installing missing dependencies; your password may be requested.'
        local -a packages=()
        local dependency
        while IFS= read -r dependency; do
            packages+=("${dependency%%[\<\>\=]*}")
        done <<< "$missing"
        sudo pacman -S --needed "${packages[@]}" </dev/tty
        pacman -T "${required[@]}" >/dev/null || {
            echo 'Dependencies are still unmet. Update Omarchy, then retry.' >&2
            return 1
        }
    fi
    python "$work/game/install.py" "${installer_args[@]}"
}

# Keep the whole script parsed before running, including when piped into bash.
main "$@"
