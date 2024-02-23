"""
Python tools for the validityBase (vBase) platform
"""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

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
        "": ["../requirements.txt", ".env", "tests/*.py"],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
