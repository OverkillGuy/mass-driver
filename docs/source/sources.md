# Sources

## Discovering repos using a Source

```{include} ../../README.md
---
start-after: "## Discovering repos using a Source"
end-before: "## Using the scanners"
```

## Creating a Source

Sources are mass-driver plugins that map to
{py:obj}`mass_driver_core.repository.Source`. Let's create one.

First, we import relevant bits:

```python
from mass_driver_core.repository import IndexedRepos, SourcedRepo, RepoUrl, Source
```

Remembering that:

```python
IndexedRepos = dict[RepoID, SourcedRepo]
```

So we now write up a new class:

```{literalinclude} ../../src/mass_driver/sources/simple.py
---
language: python
pyobject: RepolistSource
```

This class, taking a parameter `repos`, generates
{py:obj}`~mass_driver_core.repository.SourcedRepo` objects when calling
{py:meth}`~mass_driver_core.repository.Source.discover`, as a dictionary
indexed by {py:obj}`~mass_driver_core.repository.RepoID` (basically a string).

The only constraint on {py:obj}`~mass_driver_core.repository.RepoID` (type
being an alias of `str`) is that the string key is unique, so in this case we
use the `git clone` URL, which is guaranteed unique. Smarter Sources will use
something shorter, as adequate.

:::{admonition} Don't use `str` for secret fields!
:class: danger

When passing sensitive config like API tokens, you should ensure that dumping
the mass-driver config doesn't disclose any secret value. Pydantic has specific
types for that, providing the {py:obj}`pydantic.SecretStr` type, see [Pydantic
docs on Secret
fields](https://docs.pydantic.dev/1.10/usage/types/#secret-types). These field
types never print their content when represented as string, requiring a call to
`my_secret_field.get_secret_value()` to actually disclose the secret.
:::

Note the `patch_data` field of {py:obj}`~mass_driver_core.repository.SourcedRepo`,
unused in this sample Source, is an arbitrary dictionary under the
{py:obj}`~mass_driver_core.repository.Source`'s control, perfect to provide
per-repo data extracted from the source that will be relevant to make migration
against; For instance the file name to fix from some reporting tool...

To package this plugin for running it, we add it to the `pyproject.toml`
plugins:

```toml
[tool.poetry.plugins.'massdriver.sources']
repo-list = 'mass_driver.sources.simple:RepolistSource'
```

Prove it is available via `mass-driver sources`:

```{program-output} poetry run mass-driver sources
```

```{note}
For a more elaborate Source, take a look at the `pyGithub`-enabled {py:obj}`~mass_driver.sources.github_source.GithubPersonalSource`, using inheritance to enable two auth methods for `pyGithub`, using envvars for secret tokens.
```

## Testing a Source

There is no particular way to test a `Source` other than using `pytest` on your
own.

This is because Sources are usually API calls of sorts, which are hard to test
for, because of the requirement to mock API calls, and the lack of realism this
provides.

```{warning}
The Source subsystem, compared to other mass-driver plugins, bubbles up exceptions to the root, aborting any ongoing activity if left unchecked.
This is because the repo discovery process is a critical part of mass-driver runs: with no proper list of repo, there is nothing to patch over!
Compare to other plugins, where a single PatchDriver erroring over a single repo does not compromise other migrations on other repos.
```
