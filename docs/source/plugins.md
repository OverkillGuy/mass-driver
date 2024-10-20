# Available Plugins

Mass-driver uses a plugin system (aka the Python "entrypoints" system) for
discovering and loading components from third parties.

The components are available via the following entrypoint name:

| Mass-driver Component                                   | Python entrypoint     |
|---------------------------------------------------------|-----------------------|
| {py:class}`~mass_driver_core.patchdriver.PatchDriver` | `massdriver.drivers`  |
| {py:class}`~mass_driver_core.forge.forge`             | `massdriver.forges`   |
| {py:class}`~mass_driver_core.scan.ScannerFunc`        | `massdriver.scanners` |
| {py:class}`~mass_driver_core.repository.Source`       | `massdriver.sources`  |

We've packaged separately some plugins in
[mass-driver-plugins](https://github.com/OverkillGuy/mass-driver-plugins), have
a look there too.

These are the drivers that are packaged in by default:

```{jinja} plugins
---
file: templates/plugins.md.jinja2
```
