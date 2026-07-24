# Python Dependency Hashes

Development, docs, and lock-tooling dependencies use pip-tools input files plus
generated hash-locked output files. Package runtime dependencies are range-based
because `vbase-py-tools` is an intermediate installable package.

## Pattern

- Package runtime dependencies live in `requirements/base.in` and are not generated
  into a root hash lock.
- Generated terminal-environment locks include `--hash` entries.
- Install generated locks with `python -m pip install --require-hashes -r <file>`.
- Do not edit generated lock files by hand.
- The public vBase SDK dependency is installed from PyPI as a range dependency.

`setup.py` reads package runtime dependencies from `requirements/base.in`. Keep
this file free of exact pins and hash syntax so downstream applications can
resolve their full dependency graph.

## Files

- `requirements/base.in`: package runtime dependency ranges.
- `requirements/dev.in` -> `requirements/dev.txt`: development tooling.
- `requirements/docs.in` -> `requirements/docs.txt`: Sphinx docs build,
  including runtime dependencies needed to import documented tools.
- `requirements/tools.in` -> `requirements/tools.txt`: pinned pip-tools setup.

## Regeneration

Use the pinned lock tooling:

```bash
python -m pip install --require-hashes -r requirements/tools.txt
```

Regenerate locks with the Python version used by
`.github/workflows/python-dependency-locks.yml`:

```bash
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/dev.txt requirements/dev.in
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/docs.txt requirements/docs.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/tools.txt requirements/tools.in
```
