"""Driver discovery system via plugins"""

import sys

from mass_driver.model import PatchDriver

if sys.version_info < (3, 10):
    from importlib_metadata import EntryPoint, entry_points
else:
    from importlib.metadata import EntryPoint, entry_points

DriverName = str


def discover_drivers() -> list[EntryPoint]:
    """Discover all Drivers via plugin system"""
    return entry_points(group="massdriver.drivers")


def load_drivers(discovered_drivers: list[EntryPoint]) -> dict[DriverName, PatchDriver]:
    """Load all discovered drivers as map of name->callable"""
    return {driver.name: driver.load() for driver in discovered_drivers}
