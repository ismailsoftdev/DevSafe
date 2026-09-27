# Releasing DevSafe

Releases are published to PyPI by GitHub Actions (`.github/workflows/ci.yml`)
using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no
API token is stored in the repository.

## One-time setup

1. **PyPI**: sign in at <https://pypi.org>, go to *Your projects → Publishing*,
   and add a *pending publisher*:
   - PyPI project name: `devsafe`
   - Owner: `ismailsoftdev`
   - Repository name: `DevSafe`
   - Workflow name: `ci.yml`
   - Environment name: `pypi`
2. **TestPyPI**: do the same at <https://test.pypi.org> with environment name
   `testpypi`.
3. **GitHub**: in the repository's *Settings → Environments*, create
   environments named `pypi` and `testpypi`. Adding yourself as a required
   reviewer on `pypi` makes every release wait for your approval.

## Each release

1. Update the version in `devsafe/__init__.py` (the only place it is defined).
2. In `CHANGELOG.md`, replace `Unreleased` with today's date.
3. Commit and push to `main`, and wait for CI to pass.
4. Rehearse on TestPyPI: *Actions → CI → Run workflow* on `main`. Then check it installs:

   ```bash
   uv tool install --index https://test.pypi.org/simple/ \
     --index-strategy unsafe-best-match devsafe==X.Y.Z
   devsafe --version
   uv tool uninstall devsafe
   ```

5. Tag and push. CI refuses to publish if the tag doesn't match the version:

   ```bash
   git tag -a vX.Y.Z -m "DevSafe X.Y.Z"
   git push origin vX.Y.Z
   ```

6. Once the workflow finishes, verify with `uvx devsafe@X.Y.Z --version`.

PyPI never accepts the same version twice, so if a release is broken, fix it
and publish a new version.
