# Patch Drivers

Below are listed the Patch Drivers (shortened to "drivers") available at time of
docs generation. Note that drivers are expected to be coming from third parties,
and are exposed as "plugins" (also known as python package entry_points).

## Making your own driver

The simplest way to make something custom is to reconfigure an existing Driver.

See for instance the driver {py:class}`mass_driver.drivers.counter.Counter`, which
takes as configuration a `counter_file` parameter, and a `target_count`.

But if you want to do something more elaborate, you'll want your own
`PatchDriver`, exposed as a plugin.

### Defining a PatchDriver

Simply create a class that inherits from
{py:class}`mass_driver.models.patchdriver.PatchDriver`, storing any kind of configuration as
slots, and exposing a single `run` method:

```python
from mass_driver.models.patchdriver import PatchDriver, PatchResult, PatchOutcome
from mass_driver.models.repository import ClonedRepo

class PerlPackageBumper(PatchDriver):
    """Bump version of Perl packages"""

    # Each of these are parameters to tweak per migration
    # Set them under [mass-driver.migration.driver_config]
    package_target: str
    package_version: str

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Run the package bumper"""
        packages = get_packages()
        if self.package_target not in packages:
            # Do set PatchResult.details to explain not-applicable or errors
            return PatchResult(outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                               details="Package not present, no need to bump")
        version = packages[self.package_target]
        if version == self.package_version:
            return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
        # Version different from now on
        set_package_version(packages, self.package_target, self.package_version)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
```

This class is now a valid Driver, but we need to package it to make it visible
to Mass Driver.

### Packaging a driver for plugin discovery

Using the [creating a plugin via package metadata
Guide](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata),
tweaked for Poetry usage (note Poetry isn't required, just convenient):

In your `pyproject.toml`, add the following entry:

```toml
[tool.poetry.plugins.'massdriver.drivers']
perlbump = 'mypackage.mymodule:PerlPackageBumper'
```

The key here is we're declaring a new plugin called `perlbump`, part of
`massdriver.drivers`.

If you're more of a `setup.py` person, follow [the equivalent instructions for setup.py](https://github.com/python-poetry/poetry/issues/927#issuecomment-1232254538)

### Using our new plugin

Now that the plugin is declared, install your package, then use the `mass driver
drivers --list` to see if the `perlbump` driver is discovered.

Once it is, you can follow the [using mass-driver](usage) docs to execute it.

### Testing and validating a PatchDriver

Obviously, we don't recommend testing a mass-PR tool in production by cloning hundreds of repos.

We've set up some unit-level tests for PatchDriver, to be able to validate offline that a driver is working.

These tests focus on individual file transformation, which is a very common usecase.

Here's the layout of the `tests/` folder we'll be using:

```
├── test_counterdriver
│   ├── count_to_1
│   │   ├── input.txt
│   │   ├── migration.toml
│   │   └── outcome.txt
│   └── count_to_2
│       ├── input.txt
│       ├── migration.toml
│       └── output.txt
└── test_counterdriver.py
```

Note that the actual `pytest` test is `test_counterdriver.py`, with a similarly named folder `test_counterdriver/` containing 2 folders.

The pattern of testing we use here is to try transforming `input.txt` via mass-driver (configured by `migration.toml`), checking patching is successful (`PatchOutcome.PATCHED_OK`), and comparing the resulting file to `output.txt`, flagging any differences as test failures.

Optionally, presence of an `outcome.txt` will be used to check what outcome to expect instead (from the `PatchOutcome` Enum).

Similarly, the presence of a `details.txt` will be used to check the
`PatchResult.details` field, with the check: `details_txt in result.details`.

As for the test code in `pytest` to trigger all this:

```{literalinclude} ../../src/mass_driver/tests/test_counterdriver.py
---
start-after: "# test-start marker"
end-before: "# test-end marker"
---
```

The key here is use of the test fixture {py:func}`mass_driver.tests.fixtures.massdrive_check_file`, which takes a folder with these text files, and runs mass-driver over it.

For more granular, custom testing, the fixture
{py:func}`mass_driver.tests.fixtures.massdrive`, can run mass-driver CLI in a
prepackaged way, returning just
{py:class}`mass_driver.models.activity.MigrationOutcome` +
{py:class}`mass_driver.models.activity.ForgeResult` (if any forge defined) +
{py:class}`mass_driver.models.activity.ScanResult` (if any scans defined).

## Available drivers

(available-drivers)=

We've packaged separately some drivers in
[mass-driver-plugins](https://github.com/OverkillGuy/mass-driver-plugins), have
a look there too.

These are the drivers that are packaged in by default:

```{jinja} drivers
---
file: templates/drivers.md.jinja2
```
