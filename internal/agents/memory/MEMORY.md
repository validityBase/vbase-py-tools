# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- The old local `.github/actions/setup-python-deps` action was removed after docs publishing moved to the shared reusable workflow.
- Docs publishing installs `requirements/docs.txt`, builds Markdown with Sphinx, and publishes to the `main` branch of the central docs repository.

## Python Dependencies
- Runtime package dependencies are declared as ranges in `requirements/base.in`; `setup.py` reads this input file for package metadata.
- Generated development, docs, and lock-tooling files include hashes and are installed with `python -m pip install --require-hashes -r <file>`.
- `requirements/tools.txt` pins pip-tools for lock regeneration.
- The public vBase SDK dependency is installed from PyPI as a range dependency, not from the `validityBase/vbase-py` Git repository.
