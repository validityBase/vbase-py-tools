# GitHub Actions

## Policy
- Third-party actions are pinned by full commit SHA for reproducibility.
- Shared vBase-owned actions and reusable workflows use `validityBase/vbase-github-actions` with reviewed release tags such as `@v1`.
- Workflow permissions are declared explicitly and kept minimal.
- Secrets must come from GitHub Secrets or deployment configuration, never from committed files or logs.

## Workflows

### `.github/workflows/update-main-docs.yml`
- Runs on pushes to `main` and manual dispatch.
- Delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Installs `requirements/docs.txt` with Python 3.11.
- Builds Sphinx Markdown docs into `docs/_build/markdown`.
- Publishes `docs/_build/markdown` to the `main` branch of the central docs repository.
- Uses `DOCS_REPO_ACCESS_TOKEN` for the central docs repository.

### `.github/workflows/python-dependency-locks.yml`
- Runs on pull requests that modify Python dependency inputs or generated locks.
- Uses `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1`.
- Regenerates development, docs, and lock-tooling requirement locks with hashes.
- Installs generated locks with `require-hashes: "true"` and checks package metadata with `pip check`.

### `.github/workflows/repo-backup.yml`
- Runs daily and through manual dispatch to create a full-history git bundle
  backup.
- Delegates to `validityBase/vbase-github-actions/.github/workflows/repo-backup.yml@v1`.
- Uses reviewed moving major tags for validityBase-owned shared workflows so
  centrally reviewed fixes roll forward without per-repository pin updates.
- Requires `VBASE_COMMON_REPO_READ_TOKEN` and
  `VBASE_REPO_BACKUP_SECRETS_TOKEN` GitHub Actions secrets.
- Reads object storage credentials from the `vbase-repo-backups` Bitwarden
  project at runtime; bucket lifecycle and restore-test policy live outside
  this repository.
