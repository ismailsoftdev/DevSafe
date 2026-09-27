# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-09-27

- Per-directory and per-repository profiles: `devsafe bind <profile> [path]` makes every repository inside a directory use a profile, whatever profile is active globally. Also `devsafe unbind` and `devsafe bindings`. Uses git's `includeIf "gitdir:..."`, so it applies in every git client; the most specific binding wins.
- The pre-commit hook checks commits against the directory's bound profile.
- `devsafe current` shows the identity that applies in the current directory, which profile it comes from, and the config file that sets it.
- Removing a profile also removes its bindings.

## [0.1.0] - 2026-09-27

Initial public release.

- Profile management CLI: `add`, `list`, `switch`, `current`, `remove`, `init`, `status`.
- Pre-commit hook that blocks commits when git's identity doesn't match the active profile. The installed hook is a small shell script that runs `devsafe hook pre-commit`, so upgrading DevSafe updates the check in every repository; it works in GUI git clients without `devsafe` on PATH, and skips the check (with a warning) if DevSafe is uninstalled.
- `devsafe init` works from repository subdirectories and worktrees, honors `core.hooksPath`, and won't overwrite an existing hook without `--force` (which backs it up first).
- Switching to a profile without a GPG key clears the previous profile's signing settings.
- A config file that can't be loaded is reported instead of being treated as empty, so profiles are never silently overwritten.
- Requires Python 3.10+. Install from GitHub with `uv tool install git+https://github.com/ismailsoftdev/DevSafe` or pipx.
