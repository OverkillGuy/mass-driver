# Mass Driver
![PyPI](https://img.shields.io/pypi/v/mass-driver)
![PyPI - License](https://img.shields.io/pypi/l/mass-driver)

Send bulk repo change requests.

This repository is on Github: [Overkillguy/mass-driver](https://github.com/OverkillGuy/mass-driver/).

Requires Python 3.11.
## Usage

See also the docs at [jiby.tech/mass-driver/](https://jiby.tech/mass-driver/)

### Installation

Install the package:

    pip install mass-driver

We recommend you install CLIs via [pipx](https://pypa.github.io/pipx/), for dependency isolation:

    pipx install mass-driver

If you want to install from a git branch rather than Pypi:

    pipx install https://github.com/OverkillGuy/mass-driver
    # See pipx docs: https://pypa.github.io/pipx/#running-from-source-control

### Running the tool

Use the help menu to start with:

    mass-driver --help

### Preparing a change

Let's prepare for doing a change over dozens of repositories.
We'll need to find a `PatchDriver` that suits our needs, and configure it accordingly.

List available `PatchDriver`s via:

    mass-driver drivers --list
    # The docs for a single driver:
    mass-driver driver --info counter

Remember, `PatchDriver`s are exposed via a python plugin system, which means anyone can package their own!

Once you've got a driver, you should create a Migration file, in TOML:

``` toml
# Saved as "fix_teamname.toml"
[mass-driver.migration]
# As seen in 'git log':
commit_message = """Change team name

Team name XYZ is wrong, we should be called ABC instead.
See JIRA-123[1].

[1]: https://example.com/tickets/JIRA-123
"""

# Override the local git commit author
commit_author_name = "John Smith"
commit_author_email = "smith@example.com"

branch_name = "fix-team-name"

# PatchDriver class to use.
# Selected via plugin name, from "massdriver.drivers" entrypoint
driver_name = "teamname-changer"

# Config given to the PatchDriver instance
driver_config = { filename = "catalog.yaml", team_name = "Core Team" }

# Note: No "forge" section = no forge activity to pursue (no PR will be created)
```

With this file named `fix_teamname.toml` in hand, we can apply the change
locally, either against a local repo we've already cloned:

``` shell
mass-driver run fix_teamname.toml --repo-path ~/workspace/my-repo/
```
Or against a repo being cloned from URL:

``` shell
mass-driver run fix_teamname.toml --repo-path 'git@github.com:OverkillGuy/sphinx-needs-test.git'
```

The cloned repo will be under `.mass_driver/repos/USER/REPONAME/`.
We should expect a branch named `fix-team-name` with a single commit.

To apply the change over a list of repositories, create a file with relevant
repos:

``` shell
cat <<EOF > repos.txt
git@github.com:OverkillGuy/sphinx-needs-test.git
git@github.com:OverkillGuy/speeders.git
EOF

mass-driver run fix_teamname.toml --repo-filelist repos.txt
```

### Creating PRs

Once the commits are done locally, let's send them up as PR a second step.
For this, we'll be creating a second activity file containing a Forge definition.

Similarly, forges can be listed and detailed:

```shell
mass-driver forges --list
# The docs for a single forge:
mass-driver forge --info counter
```

Consider using the `forge_name = "github"`.
Create a new Activity with a Forge:

``` toml
# An Activity made up of just a forge
[mass-driver.forge]
forge_name = "github"

base_branch = "main"

head_branch = "fix-teamname"
draft_pr = true
pr_title = "[JIRA-123] Bump counter.txt to 1"
pr_body = """Change team name

Team name XYZ is wrong, we should be called ABC instead.
See JIRA-123[1].

[1]: https://example.com/tickets/JIRA-123
"""

# Do you need to git push the branch before PR?
git_push_first = true
```

Now run mass-driver, remembering to set the `FORGE_TOKEN` envvar for a Github/other auth token.

``` shell
export FORGE_TOKEN="ghp_supersecrettoken"
mass-driver run fix_teamname_forge.toml --repo-filelist repos.txt
```

### Combining migration then forge
Sometimes, we wish to expedite both the committing and the PR creation in a single move.

The Activity file can contain both sections:

``` toml
# An activity made up of first a Migration, then a Forge
[mass-driver.migration]
# As seen in 'git log':
commit_message = """Change team name

Team name XYZ is wrong, we should be called ABC instead.
See JIRA-123[1].

[1]: https://example.com/tickets/JIRA-123
"""

# Override the local git commit author
commit_author_name = "John Smith"
commit_author_email = "smith@example.com"

branch_name = "fix-team-name"

# PatchDriver class to use.
# Selected via plugin name, from "massdriver.drivers" entrypoint
driver_name = "teamname-changer"

# Config given to the PatchDriver instance
driver_config = { filename = "catalog.yaml", team_name = "Core Team" }

# And a forge = PR creation after Migration
[mass-driver.forge]
forge_name = "github"

base_branch = "main"

head_branch = "fix-teamname"
draft_pr = true
pr_title = "[JIRA-123] Bump counter.txt to 1"
pr_body = """Change team name

Team name XYZ is wrong, we should be called ABC instead.
See JIRA-123[1].

[1]: https://example.com/tickets/JIRA-123
"""

# Do you need to git push the branch before PR?
git_push_first = true

```
<!-- source-activity -->
### Discovering repos using a Source


Sometimes, the repos we want to apply patches to is a dynamic thing, coming from
tooling, like a Github repository search, some compliance tool report, service
catalogue, etc.

To address this, mass-driver can use a Source plugin to discover repositories to
apply activities to.

``` toml
# An Activity file with a file-list Source
[mass-driver.source]
source_name = "repo-list"
# Source 'repo-list' takes a 'repos' list of cloneable URLs:
[mass-driver.source.source_config]
repos = [
  "git@github.com:OverkillGuy/mass-driver.git",
  "git@github.com:OverkillGuy/mass-driver-plugins.git",
]
```

Because we included a `Source`, we can omit the CLI flags `--repo-path` or
`--repo-filelist`, to instead rely on the activity's config to discover the
repos.

``` shell
mass-driver run activity.toml
```

Smarter Sources can use more elaborate parameters, maybe even secret parameters
like API tokens.

To pass secrets safely, config parameters passed via `source_config` in file
format can be passed as envvar, using prefix `SOURCE_`. So we could have avoided
the `repos` entry in file, by providing a `SOURCE_REPOS` envvar instead. This
feature works because the Source class derives from `Pydantic.BaseSettings`.


### Using the scanners
Before doing any actual migration, we might want to explore existing repositories to see what kind of change is required.

Mass-driver provides for this usecase via the scanners plugin system, enabling a simple python function to be run against many repos, with the purpose of gathering information.

<!-- scanner-activity -->
Let's define an Activity file specifying a list of scanners to run:

``` toml
# An Activity file for scanning
[mass-driver.scan]
scanner_names = ["root-files", "dockerfile-from"]
```
This can be run just like a migration:

``` shell
mass-driver run scan.toml --repo-filelist repos.txt
```


## Development

### Python setup

This repository uses Python3.11, using
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
