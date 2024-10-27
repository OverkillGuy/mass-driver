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
    "sphinx.ext.viewcode",
    "sphinx_jinja",
    "myst_parser",
    "autodoc2",
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


autodoc2_packages = [
    "../../src/mass_driver",
]
# Enable all docstrings as Myst Markdown
autodoc2_docstring_parser_regexes = [
    (r".*", "myst"),
]

myst_heading_anchors = 2
myst_enable_extensions = ["substitution", "colon_fence"]


# https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#customising-external-url-resolution
myst_url_schemes = {
    "http": None,
    "https": None,
    "rfc": "https://datatracker.ietf.org/doc/html/rfc{{path}}"
    # "gh-issue": {
    #     "url": "https://github.com/executablebooks/MyST-Parser/issue/{{path}}#{{fragment}}",
    #     "title": "Issue #{{path}}",
    #     "classes": ["github"],
    # },
}

# man_pages = [
#     # ("manpage", "mass-driver", "Send pull-requests to many repos, monitor PRs adoption", author, "1")
# ]

# Sphinx-jinja:

from mass_driver.discovery import (
    discover_drivers,
    discover_forges,
    discover_sources,
    discover_scanners,
)

plugin_discovery = {
    "drivers": discover_drivers,
    "forges": discover_forges,
    "sources": discover_sources,
    "scanners": discover_scanners,
}


plugins = {}
for plugin_type, discover_func in plugin_discovery.items():
    plugins[plugin_type] = {}
    plugins_discovered = discover_func()
    for plugin in plugins_discovered:
        plugins[plugin_type][plugin.name] = {
            "name": plugin.name,
            "module": plugin.module,
            "class_name": plugin.attr,
        }

jinja_contexts = {
    "plugins": {"plugins": plugins},
}

jinja_env_kwargs = {
    "trim_blocks": True,
}
