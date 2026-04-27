# Release Process

This project publishes to PyPI with GitHub Actions trusted publishing. No PyPI
API token is stored in GitHub.

## Policy

`master` is the release branch. Keep it stable and releasable.

Do not publish on every push to `master`. PyPI release files are immutable, so a
push without a version bump would fail, and an accidental direct push could
publish a broken package. Instead, publish from version tags on `master`.

The practical invariant is:

- the latest PyPI release must correspond to a `vX.Y.Z` tag on `master`;
- after a release, `master` and PyPI represent the same package code;
- unreleased work happens on feature branches.

## One-Time PyPI Setup

Configure a trusted publisher on PyPI for this project.

For an existing PyPI project:

1. Open `salus-it600-client` on PyPI.
2. Go to `Manage -> Publishing`.
3. Add a GitHub trusted publisher:
   - Owner: `Jordi-14`
   - Repository name: `salus-it600-client`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`

If the PyPI project does not exist yet, create a pending publisher from the PyPI
account publishing settings with the same values and project name
`salus-it600-client`.

Create a GitHub environment named `pypi`. Leave it without required reviewers if
publishing should be fully automatic after pushing a release tag. Add required
reviewers if you want a final manual approval step before PyPI upload.

## Normal Development

1. Start from `master`.
2. Create a feature or fix branch.
3. Make the code change and add tests.
4. Bump the version in both files:
   - `pyproject.toml`
   - `salus_it600/__version__.py`
5. Open and merge the branch into `master` after CI passes.

Use semantic-ish versioning:

- patch version for compatible bug fixes;
- minor version for new compatible features;
- major version only for intentional breaking changes.

## Publishing

After merging the release commit to `master`, tag that exact commit:

```bash
git switch master
git pull --ff-only origin master
python3 -m unittest
python3 -m build
python3 -m twine check dist/*
git tag v0.1.1
git push origin v0.1.1
```

The `Publish to PyPI` workflow then:

1. verifies the tag matches `pyproject.toml`;
2. verifies `pyproject.toml` and `salus_it600/__version__.py` match;
3. runs critical lint checks;
4. compiles the package;
5. runs the unit tests;
6. builds the wheel and source distribution;
7. checks both distributions with Twine;
8. publishes to PyPI through trusted publishing.

If the workflow fails before uploading, fix the branch and move the tag to the
fixed commit only if nothing was published:

```bash
git tag -f v0.1.1
git push --force origin v0.1.1
```

If any file was already uploaded to PyPI, never reuse that version. Bump to the
next version and publish a new tag.

## Direct `master` Pushes

Avoid direct pushes to `master` except for repository maintenance that is known
not to need a package release. Prefer branch protection on GitHub with required
CI checks before merge.
