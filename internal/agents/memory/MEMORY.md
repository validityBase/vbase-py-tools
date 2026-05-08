# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- The old local `.github/actions/setup-python-deps` action was removed after docs publishing moved to the shared reusable workflow.
- Docs publishing installs `docs/requirements.txt` before `requirements.txt`, builds Markdown with Sphinx, and publishes to the `main` branch of the central docs repository.
