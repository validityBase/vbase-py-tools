# vbase-py-tools

vBase Python Tools

-   Python 3.8+ support

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Introduction

This package provides a collection of Python tools for the vBase Python SDK.

vBase creates a global auditable record of when data was created, by whom, and how it has changed (collectively, “data provenance”). Data producers can prove the provenance of their data to any external party, increasing its value and marketability. Data consumers can ensure the integrity of historical data and any derivative calculations. The result is trustworthy information that can be put into production quickly without expensive and time-consuming trials.

vBase services do not require access to the data itself, assuring privacy. They also do not rely on centralized intermediaries, eliminating the technical, operating, and business risks of a trusted party controlling your data and its validation. vBase ensures data security and interoperability that is unattainable with legacy centralized systems. It does so by storing digital fingerprints of data, metadata, and revisions on secure public blockchains.

With vBase, creating and consuming provably correct data is as easy as pressing a button.

![Demo](https://github.com/validityBase/vbase-py-tools/assets/153264511/d5447b1b-79ad-48c5-89a6-828b31828b2b)

## Getting Started

Please follow the [Setup](docs/setup.md) guide to configure your environment.

Install the package from the repository:

```bash
python -m pip install -e .
```

For development tooling:

```bash
python -m pip install --require-hashes -r requirements/dev.txt
python -m pip install --no-deps --no-build-isolation -e .
```

Use the pinned lock tooling before regenerating requirements files:

```bash
python -m pip install --require-hashes -r requirements/tools.txt
```

Dependency updates should be made in the matching `.in` file, then regenerated
with the same `pip-compile` flags used in CI:

```bash
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/dev.txt requirements/dev.in
pip-compile --strip-extras --no-annotate --generate-hashes -o requirements/docs.txt requirements/docs.in
pip-compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements/tools.txt requirements/tools.in
```

Runtime package dependencies are range-based in `requirements/base.in`. Do not
edit generated lock files by hand.
