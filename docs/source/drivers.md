# Patch Drivers

Below are listed the Patch Drivers (shortened to "drivers") available at time of
docs generation. Note that drivers are expected to be coming from third parties,
and are exposed as "plugins" (also known as python package entry_points).

## Available drivers
(available-drivers)=

```{jinja} drivers
---
file: templates/drivers.md.jinja2
```


## Making your own driver

The simplest way to make something custom is to reconfigure an existing Driver.

See for instance the driver {py:class}`mass_driver.drivers.ShellDriver`, which
takes as configuration a `command` parameter, which can be any shell-compatible
command.

But if you want to do something more elaborate, you'll want your own
`PatchDriver`, exposed as a plugin.

### Defining a PatchDriver

Simply create a class that inherits from
{py:class}`mass_driver.patchdriver.PatchDriver`, storing any kind of configuration as
slots, and exposing a single `run` method:

```python
from mass_driver.patchdriver import PatchDriver

class PerlPackageBumper(PatchDriver):
    """Bump version of Perl packages"""

    package_target: str
    package_version: str

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Run the package bumper"""
        packages = get_packages()
        if self.package_target not in packages:
            return False  # Didn't need to bump package: no such package present
        if dry_run:
            return True  # Stop before actually doing the thing
        set_package_version(packages, self.package_target, self.package_version)
        return True  # Repo changes were indeed needed + done
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
