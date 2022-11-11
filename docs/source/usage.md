# Using mass-driver


## Installation

```
pip install mass-driver??? Not uploaded to Pypi
```

## Usage


### Full help message

```{program-output} poetry run mass-driver --help
```

### Selecting repos

First, provide a list of repositories to look up.
This can be done either via successive `--repo-path` invocations on the fly,
```sh
mass-driver \
    --repo-path "git@github.com:OverkillGuy/sphinx-needs-test.git"\
    --repo-path "git@github.com:OverkillGuy/literate-wordle.git"
```
 or
as a newline-delimited file:
```sh
# Create a list of repos
cat <<EOF > repos.txt
git@github.com:OverkillGuy/sphinx-needs-test.git
git@github.com:OverkillGuy/literate-wordle.git
EOF

mass-driver --repo-filelist repos.txt
```

Remember that repo paths can be either URLs to clone from, or existing paths on
local directories, so the following does work:

```sh
mass-driver --repo-path ~/workspace/java_project2
```
### Configuring a driver


Head over to [mass_driver.Drivers](autoapi/mass_driver/drivers/index) and pick
a driver.

WIP (driver selection is not yet exposed in CLI)


### Dry run

The default run mode is to only detect the change to be done, no destructive
action.
To make local commits (no pushes), you'll need to disable dry-run mode:

```sh
mass-driver --repo-filelist repos.txt --really-commit-changes
```

## Sample output

For a dry-run invocation like this:
```shell
poetry run mass-driver --dry-run --repo-filelist repos
```

The outcome is:
```{code-block} none
Processing 2 with driver=Poetry(package='pytest', target_major='8', package_group='test')
[001/002] Processing /home/jiby/dev/ws/short/sliding-puzzle-solver/...
Given an existing (local) repo: no cloning
Detecting '/home/jiby/dev/ws/short/sliding-puzzle-solver/' before patching...
Didn't find pytest in pyproject.toml test deps!
Does not need patching: skipping
[002/002] Processing git@github.com:OverkillGuy/literate-wordle.git...
Given a URL, cache miss: cloning
Detecting 'git@github.com:OverkillGuy/literate-wordle.git' before patching...
Didn't find pytest in pyproject.toml test deps!
Does not need patching: skipping
Action completed: exiting
```
