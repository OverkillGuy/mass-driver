# Configuration file for the Sphinx documentation builder.

#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "Mass Driver"
copyright = "2022, Jb Doyon"
author = "Jb Doyon"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx_jinja",
    "autoapi.extension",
    "myst_parser",
    "sphinxcontrib.programoutput",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


autoapi_type = "python"
autoapi_dirs = ["../../src"]

# Do not hijack toctree to add entry
autoapi_add_toctree_entry = False

# Make sure the target is unique
autosectionlabel_prefix_document = True

myst_heading_anchors = 2
myst_enable_extensions = ["substitution"]

man_pages = [
    ("manpage", "mass-driver", "Send pull-requests to many repos, monitor PRs adoption", author, "1")
]

# Sphinx-jinja:

from mass_driver.discovery import discover_drivers

discovered_drivers = discover_drivers()
drivers = {}
for driver in discovered_drivers:
    drivers[driver.name] = {"name": driver.name,
                            "module": driver.module,
                            "class_name": driver.attr,
                            # "class": driver_class,
                            }

jinja_contexts = {
    'drivers': {"drivers": drivers},
}

jinja_env_kwargs = {
    'trim_blocks': True,
}
