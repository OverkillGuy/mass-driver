# Sources

```{include} ../../README.md
---
start-after: "<!-- source-activity -->"
end-before: "### Using the scanners"
```

### Creating a Source

Sources are mass-driver plugins that map to
{py:obj}`mass_driver.models.source.Source`. Let's create one.

First, we import relevant bits:

```python
from mass_driver.models.source import IndexedRepos, Repo, RepoUrl, Source
```
Remembering that:

```python
IndexedRepos = dict[RepoID, Repo]
```

So we now write up a new class:

```{literalinclude} ../../src/mass_driver/sources/simple.py
---
language: python
pyobject: RepolistSource
```

This class, taking a parameter `repos`, generates
{py:obj}`mass_driver.models.source.Repo` objects when calling `discover()`, as a
dictionary indexed by {py:obj}`mass_driver.models.source.RepoID` (basically a
string).

The only constraint on `RepoID` is that the string key is unique, so in this
case we use the `git clone` URL, which is guaranteed unique. Smarter Sources
will use something shorter, as adequate.

Note the `patch_data` field of `Repo`, unused in this sample Source, is an
arbitrary dictionary under the `Source`'s control, perfect to provide per-repo
data extracted from the source that will be relevant to make migration against;
For instance the file name to fix from some reporting tool...

To package this plugin for running it, we add it to the `pyproject.toml`
plugins:

```toml
[tool.poetry.plugins.'massdriver.sources']
repo-list = 'mass_driver.sources.simple:RepolistSource'
```

Prove it is available via `mass-driver sources`:

```{program-output} poetry run mass-driver sources
```

### Testing a Source

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
