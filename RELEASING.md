# Releasing DevSafe

DevSafe is distributed from GitHub: users install from the repository
(`uv tool install git+https://github.com/ismailsoftdev/DevSafe`), and
`uv tool upgrade devsafe` / `pipx upgrade devsafe` gets the latest `main`.
Every push to `main` therefore reaches users on their next upgrade; keep it
green.

A release is a version tag. When a `vX.Y.Z` tag is pushed, CI
(`.github/workflows/ci.yml`) runs the tests, checks the tag matches the
package version, and creates a GitHub Release with the wheel and sdist
attached. Users can install that exact version with
`uv tool install git+https://github.com/ismailsoftdev/DevSafe@vX.Y.Z`.

## Each release

1. Update the version in `devsafe/__init__.py` (the only place it is defined).
2. In `CHANGELOG.md`, replace `Unreleased` with today's date.
3. Commit and push to `main`, and wait for CI to pass.
4. Tag and push:

   ```bash
   git tag -a vX.Y.Z -m "DevSafe X.Y.Z"
   git push origin vX.Y.Z
   ```

5. Once the workflow finishes, check the release page and verify:

   ```bash
   uvx --from git+https://github.com/ismailsoftdev/DevSafe@vX.Y.Z devsafe --version
   ```

If a release is broken, fix it and release a new version rather than moving
the tag; pinned installs expect tags not to change.

## When the repository goes public

Installing from GitHub keeps working unchanged, and the authentication
section in INSTALL.md can be removed. Publishing to PyPI as well (for
`uv tool install devsafe` / `pipx install devsafe`) is optional: commit
6f95c2b has a ready-made Trusted Publishing workflow and setup steps to
restore.
