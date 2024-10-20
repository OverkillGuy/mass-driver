# Project Objectives

This project is trying to do the following (from Gherkin Features described in
the project's `features/` folder).

Note this page is not exhaustive, it's just trying to showcase some of the
capabilities we wished existed.

## Creating patches

```{literalinclude} ../../features/create_patch.feature
---
language: gherkin
---
```

In practice, we can assume a {py:obj}`~mass_driver_core.source.Source` that
can discover repos using `libxml`, and a
{py:obj}`~mass_driver_core.patchdriver.PatchDriver` for bumping packages,
triggering a PR via {py:obj}`~mass_driver_core.forge.Forge`.

## Migration Lifecycle

```{literalinclude} ../../features/migration_lifecycle.feature
---
language: gherkin
---
```

## Repo discovery

```{literalinclude} ../../features/repo_discovery.feature
---
language: gherkin
---
```

This is the dream of {py:obj}`~mass_driver_core.source.Source` plugins, as
described in [Sources](./sources)
