"""
Python tools for the validityBase (vBase) platform
"""

from pathlib import Path

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_REQUIREMENTS_FILE = ROOT_DIR / "requirements/base.in"

long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")

requirements = []
for raw_line in PACKAGE_REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
    line = raw_line.split("#", 1)[0].strip()
    if not line or line.startswith("-"):
        continue
    requirements.append(line)

setup(
    name="c2tools",
    version="0.0.1",
    author="PIT Labs Inc.",
    author_email="tech@pitlabs.xyz",
    description="Python tools for the validityBase (vBase) platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/validityBase/vbase-py-tools",
    packages=find_packages(),
    package_data={
        "": ["tests/*.py"],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
