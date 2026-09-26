# Release notes

## 1.1.0

- Add Xbox-style controller support on desktop and web, including menus,
  cinematics, continue screens, and the browser's first loading screen.
- Aim and fire in eight directions with the left stick or D-pad; use the right
  stick for independent aiming, including the final space encounter.
- Add adjustable stick deadzone, controller prompts, GameSir G7 SE mapping,
  focus/disconnect protection, and safe held-button handling between scenes.
- Launch the browser version with shared desktop gameplay and cinematics.
- Improve the guardian-to-dragon transition and soften the title Start explosion.

## 1.0.2

- Fix held keys replaying actions across scene changes and missed input after
  returning to the game from another window.
- Keep firing through double-clicks and preserve shot timing across frames.
- Prevent lingering guardian projectiles from hitting after a guardian is defeated.
- Correct harbor damage tracking for unlimited-lives runs.
- Recover safely from invalid saved settings and improve launcher path escaping.
- Harden preview tools and separate development checks from release checksum checks.
- Thanks to Fred Nix (@nixfred) for the fixes in [PR #1](https://github.com/gardnmi/omacontra/pull/1).

## 1.0.1

- Fix installation when a virtual environment, mise, or pyenv shadows system
  Python: use Arch’s system interpreter for GI and Cairo dependencies.
- Ignore PYTHONHOME, PYTHONPATH, and user-site packages in installed launchers.
- Include the interpreter path in missing-dependency diagnostics.

## 1.0.0

First public release for Omarchy / Hyprland.

- Five boss encounters with story cinematics, Standard and Hardcore modes.
- Persistent results, stage medals, personal bests, and a soundtrack player.
- Keyboard and mouse controls; 720p internal rendering scaled to your display.
- Standalone installer and Arch package, with no AUR requirement.
- Includes the final guardian boundaries, wider dragon fireball spread, and
  corrected spaceship boarding hatch from release-candidate testing.

See [support and known limitations](SUPPORT.md) and the
[asset credits and terms](../THIRD_PARTY/ASSET_RIGHTS.md).

## 0.1.0-rc.3

- Move the spaceship hatch below the cockpit glass and align the elevator stop,
  walkway, and boarding animation with the new entrance.

## 0.1.0-rc.2

- Wider gaps between the dragon’s first-phase eye fireballs make platform crossings
  more forgiving. Projectile speed, volley size, laser rotation, and second-phase
  attacks retain their existing tuning.

## 0.1.0-rc.1

First release candidate for Omacontra on Omarchy / Hyprland.

- Five boss encounters, story cinematics, Standard and Hardcore modes.
- Persistent results, personal bests, stage medals, and a soundtrack player.
- Shuffled gameplay music and a dedicated finale track.
- Fixed 1280 × 720 internal rendering, scaled to the display.
- Direct installer and standalone Arch package; no AUR requirement.
- Version displayed in menus and through `omacontra --version`.
- Installer status messages for verification, extraction, dependencies, and installation.
- Unlimited-lives code works throughout the opening cinematic and on the title screen.
- Three harbor cargo trolleys and boundaries that prevent hiding behind the guardians.

See [known limitations and support](SUPPORT.md) before reporting a problem.
