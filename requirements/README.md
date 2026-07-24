# Python Requirements

Package dependency metadata lives in `base.in` as broad ranges. `setup.py`
reads that file for `install_requires`.

Human-edited terminal environment inputs live in `requirements/*.in`. Generated
hash-locked terminal environment files live in `requirements/*.txt`.

Do not edit generated `.txt` files by hand. Regenerate them with the documented
commands in `../internal/specs/python-dependency-hashes.md`.
