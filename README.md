# Mass Driver

Send bulk repo change requests.

This repository is on Github: [Overkillguy/mass-driver](https://github.com/OverkillGuy/mass-driver/).

Requires Python 3.10
## Usage

See the docs at [jiby.tech/mass-driver/](https://jiby.tech/mass-driver/)

### Run the command

Install the module first:

    make install
    # or
    poetry install

Then inside the virtual environment, launch the command:

    # Run single command inside virtualenv
    poetry run mass-driver

    # or
    # Load the virtualenv first
    poetry shell
    # Then launch the command, staying in virtualenv
    mass-driver

## Development

### Python setup

This repository uses Python3.10, using
[Poetry](https://python-poetry.org) as package manager to define a
Python package inside `src/mass_driver/`.

`poetry` will create virtual environments if needed, fetch
dependencies, and install them for development.


For ease of development, a `Makefile` is provided, use it like this:

	make  # equivalent to "make all" = install lint docs test build
	# run only specific tasks:
	make install
	make lint
	make test
	# Combine tasks:
	make install test

Once installed, the module's code can now be reached through running
Python in Poetry:

	$ poetry run python
	>>> from mass_driver import main
	>>> main("blabla")


This codebase uses [pre-commit](https://pre-commit.com) to run linting
tools like `flake8`. Use `pre-commit install` to install git
pre-commit hooks to force running these checks before any code can be
committed, use `make lint` to run these manually. Testing is provided
by `pytest` separately in `make test`.

### Documentation

Documentation is generated via [Sphinx](https://www.sphinx-doc.org/en/master/),
using the cool [myst_parser](https://myst-parser.readthedocs.io/en/latest/)
plugin to support Markdown files like this one.

Other Sphinx plugins provide extra documentation features, like the recent
[AutoAPI](https://sphinx-autoapi.readthedocs.io/en/latest/index.html) to
generate API reference without headaches.

To build the documentation, run

    # Requires the project dependencies provided by "make install"
    make docs
	# Generates docs/build/html/

To browse the website version of the documentation you just built, run:

    make docs-serve

And remember that `make` supports multiple targets, so you can generate the
documentation and serve it:

    make docs docs-serve

## License

This project is released under GPLv3 or later. See `COPYING` file for GPLv3
license details.

### Templated repository

This repo was created by the cookiecutter template available at
https://github.com/OverkillGuy/python-template, using commit hash: `5c882f2e22311a2307263d14877c8229a2ed6961`.
