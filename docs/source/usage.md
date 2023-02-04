# Using mass-driver


## Installation

```
pip install mass-driver??? Not uploaded to Pypi
```

## Usage

Top-level command:

```{program-output} poetry run mass-driver --help
```

Inspecting drivers:

```{program-output} poetry run mass-driver drivers --help
```

Running the actual mass driver:

```{program-output} poetry run mass-driver run-migration --help
```


### Selecting repos

First, provide a list of repositories to look up.
This can be done either via successive `--repo-path` invocations on the fly,
```sh
mass-driver run-migration \
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

mass-driver run-migration --repo-filelist repos.txt migration.toml
```

Remember that repo paths can be either URLs to clone from, or existing paths on
local directories, so the following does work:

```sh
mass-driver run-migration --repo-path ~/workspace/java_project2 migration.toml
```
### Configuring a PatchDriver, creating a Migration

Pick a driver from [available drivers](./drivers#available-drivers).

You'll need to create a Migration config file:

```{literalinclude} ../../src/mass_driver/tests/test_counterdriver/counter_config2.toml
---
language: toml
---
```

Save it and use it as `migration_file` parameter to `mass-driver run`.
### Dry run

The default run mode is to do the change, but not commit it.
To make local commits (no pushes), you'll need to disable dry-run mode:

```sh
mass-driver run migration.toml --repo-filelist repos.txt --really-commit-changes
```

## Sample output

For an invocation like this:
```shell
poetry run mass-driver run --repo-filelist repos
```

The outcome is:
```{code-block} none
Processing 2 with migration.driver=Counter(target_count=1, counter_file='counter.txt')
[001/002] Processing git@github.com:OverkillGuy/sphinx-needs-test.git...
Given a URL, cache miss: cloning
Detecting 'git@github.com:OverkillGuy/sphinx-needs-test.git' before patching...
PATCH_DOES_NOT_APPLY
Patch wasn't OK: skip commit
[002/002] Processing git@github.com:OverkillGuy/literate-wordle.git...
Given a URL, cache miss: cloning
Detecting 'git@github.com:OverkillGuy/literate-wordle.git' before patching...
PATCH_DOES_NOT_APPLY
Patch wasn't OK: skip commit
Action completed: exiting
{'git@github.com:OverkillGuy/sphinx-needs-test.git': PatchResult(outcome=<PatchOutcome.PATCH_DOES_NOT_APPLY: 'PATCH_DOES_NOT_APPLY'>, details='No counter file exists yet'), 'git@github.com:OverkillGuy/literate-wordle.git': PatchResult(outcome=<PatchOutcome.PATCH_DOES_NOT_APPLY: 'PATCH_DOES_NOT_APPLY'>, details='No counter file exists yet')}
```

## Generating PRs

Assuming you've got a list of branches ready to make PRs for, we can use `run-forge` subcommand.

```{program-output} poetry run mass-driver run-forge --help
```

The forge file looks like this:
```toml
[mass-driver]
base_branch = "main"
head_branch = "my-branch"
pr_title = "[JIRA-123] Cool PR title"
pr_body = """Some extra words as PR body
And then some more.
"""
draft = false

forge = "github"
```
