# Scanning

Mass-driver is mostly about generating bulk changes, but migrations require a
good idea of what we need to change. A good amount of thought needs to be given
to finding patterns in repositories before any change can happen.

Let's see how mass-driver scans enable exploration of our repositories by
writing simple python functions, reusable as plugins.

## Using mass-driver to scan

```{include} ../../README.md
---
start-after: "<!-- scanner-activity -->"
end-before: "## Reviewing bulk PR status"
```

## Creating a Scanner

Scanners are mass-driver plugins that map to functions. Let's create one.

First some imports:

```python
from pathlib import Path
from typing import Any
```

Then the function:

```{literalinclude} ../../src/mass_driver/scanners/basic_scanners.py
---
language: python
pyobject: dockerfile_from_scanner
```

This scanner will try to open the repo's `Dockerfile`, and if any exist, will
report lines that start with the `FROM` keyword.

Note that the scanner is built to report the same dict keys in all cases.

We suggest scanner functions return flat dictionaries (simple key, simple value,
no nesting), to make it easy to map the returned content to database-style rows
of data (or simply CSV). Try to take into account every check that can go wrong
(like missing file/folder), and find a way to report on the specific of this
repository uniquely.

To package this plugin for running it, we add it to the `pyproject.toml` plugins:

```toml
[tool.poetry.plugins.'massdriver.scanners']
dockerfile-from = 'my_lovely_package.dockerfile:dockerfile_from_scanner'
```

Prove it is available via `mass-driver scanners`:

```none
Available scanners:
root-files
dockerfile-from
```

And now we can define an activity file with our scanner toggled on, possibly as
part of other scanners.

```toml
# dockerfile_scan.toml
[mass-driver.scan]
scanner_names = ["dockerfile-from", "root-files"]
```

Now let's generate the scan reports:

```shell
mass-driver run dockerfile_scan.toml --repo-filelist repos.txt
```

## Testing the scanner

Before running it across many many repos, let's test it with sample data. For
this, we have a couple handy test fixtures available that turn testing into a
trivial matter.

So let's start by writing a new empty file `tests/test_scanner.py`, and a folder
structure like this:

```none
tests/
├── test_scanner/
│   ├── dockerfile/
│   │   ├── activity.toml
│   │   ├── Dockerfile
│   │   └── scan_results.json
│   └── multiple-dockerfiles/
│       ├── activity.toml
│       ├── Dockerfile
│       └── scan_results.json
└── test_scanner.py
```

The intent is for each subfolder under `tests/test_scanner/` to be pretend
repos, with an `activity.toml` selecting the scanners, and a `scan_results.json`
to report on the repo's scan.

As for the test file, here is the contents:

```{literalinclude} ../../src/mass_driver/tests/test_scanner.py
---
language: python
---
```

Note how the test relies on the `massdrive_scan_check` fixture to run scan
against specific folder. This wraps around the `massdrive` fixture.

```{note}
The scanner subsystem will swallow exceptions, using the `scannerror`
key to define two things: `exception: str`, and `backtrace: list[str]`.
```
