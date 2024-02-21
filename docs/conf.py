# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "c2tools"
# Drop the trailing period since Sphinx adds it.
copyright = "2023, PIT Labs Inc"
author = "PIT Labs Inc."

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_argparse_cli",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
]

# Hide the Sphinx footer text.
html_show_sphinx = False
html_show_sourcelink = False

html_theme_options = {
    "show_powered_by": "False",
}
