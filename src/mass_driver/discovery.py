"""Driver discovery system via plugins"""

import sys

from mass_driver.model import PatchDriver

if sys.version_info < (3, 10):
    from importlib_metadata import EntryPoints, entry_points
else:
    from importlib.metadata import EntryPoints, entry_points

DriverName = str


def discover_drivers() -> EntryPoints:
    """Discover all Drivers via plugin system"""
    return entry_points(group="massdriver.drivers")


def get_driver(driver_name: str) -> type[PatchDriver]:
    """Fetch the given driver class, by name"""
    drivers = discover_drivers()
    if driver_name not in drivers.names:
        raise ImportError(f"Driver '{driver_name}' not found in 'massdriver.drivers'")
    (driver,) = drivers.select(name=driver_name)
    return driver.load()
