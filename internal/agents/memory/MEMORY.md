# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Repository backup delegates to `validityBase/vbase-github-actions/.github/workflows/repo-backup.yml@v1`. Details stay in `internal/specs/github-actions.md`.
- The old local `.github/actions/setup-python-deps` action was removed after docs publishing moved to the shared reusable workflow.
- Docs publishing installs `requirements/docs.txt`, builds Markdown with Sphinx, and publishes to the `main` branch of the central docs repository.

## Python Dependencies
- Dependency layout, lock policy, and package metadata rules are canonical in
  `internal/specs/python-dependency-hashes.md`; keep that as the only detailed
  copy.
- The public vBase SDK dependency is installed from PyPI as a range dependency, not from the `validityBase/vbase-py` Git repository.
