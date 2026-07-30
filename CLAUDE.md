# CLAUDE.md

This repository contains command-line tools and documentation built on top of
the vBase Python SDK.

## Core Standards

- Keep tool code small, readable, and focused on operational workflows.
- Do not commit secrets, private keys, API tokens, `.env` files, or logs
  containing credentials.
- Dependency layout, lock policy, and package metadata rules are canonical in
  `internal/specs/python-dependency-hashes.md`; do not duplicate them here.
- Documentation published externally lives in `docs/`.
- Internal specs, guides, and agent memory live in `internal/`.

## Internal Documentation

- Agent memory: [internal/agents/memory/MEMORY.md](internal/agents/memory/MEMORY.md)
- GitHub Actions: [internal/specs/github-actions.md](internal/specs/github-actions.md)
- Python dependency hashes: [internal/specs/python-dependency-hashes.md](internal/specs/python-dependency-hashes.md)
