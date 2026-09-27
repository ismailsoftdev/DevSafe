# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - Unreleased

Initial public release.

- Profile management CLI: `add`, `list`, `switch`, `current`, `remove`, `init`, `status`.
- Pre-commit hook that blocks commits when git's identity doesn't match the active profile.
- `devsafe init` works from repository subdirectories and worktrees, honors `core.hooksPath`, and won't overwrite an existing hook without `--force` (which backs it up first).
- Switching to a profile without a GPG key clears the previous profile's signing settings.
- A config file that can't be loaded is reported instead of being treated as empty, so profiles are never silently overwritten.
- Requires Python 3.10+. Install with `uv tool install devsafe` or `pipx install devsafe`.
