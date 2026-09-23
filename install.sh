#!/usr/bin/env bash
# Direct Omarchy installer. No Git checkout or AUR account required.
set -euo pipefail

main() {
    status() { printf '\n==> %s\n' "$*"; }
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
    local release=v1.0.1
    local checksum=7e766b318c1fce2d875e16c5417787a2ce720b49e526fdc6f6305227db0cbcbd
    if [[ -n $archive ]]; then
        status 'Using local release archive'
        cp -- "$archive" "$work/game.tar.gz"
    else
        command -v curl >/dev/null || { echo 'Install curl first.' >&2; return 1; }
        status 'Downloading Omacontra (curl shows transfer progress)'
        if ! curl --fail --location --show-error --retry 3 --proto '=https' --tlsv1.2 \
            "https://github.com/gardnmi/omacontra/releases/download/$release/omacontra-runtime.tar.gz" -o "$work/game.tar.gz"; then
            echo 'Download failed. The selected GitHub release must be published and public; testers can use --archive FILE with the runtime download.' >&2
            return 1
        fi
    fi
    status 'Verifying release checksum'
    printf '%s  %s\n' "$checksum" "$work/game.tar.gz" | sha256sum --check --status || {
        echo 'Download verification failed; nothing has been installed.' >&2
        return 1
    }
    status 'Extracting game files'
    mkdir "$work/game"
    tar -xzf "$work/game.tar.gz" -C "$work/game" --strip-components=1 --no-same-owner --no-same-permissions
    status 'Checking system dependencies'
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
    if [[ $action == uninstall ]]; then
        status 'Removing installed game'
    else
        status 'Installing game files and app-menu launcher'
    fi
    /usr/bin/python -E -s "$work/game/install.py" "${installer_args[@]}"
    if [[ $action == install ]]; then status 'Ready — launch Omacontra from the apps menu or run omacontra'; fi
}

# Keep the whole script parsed before running, including when piped into bash.
main "$@"
