"""Driver discovery system via plugins"""

import sys

from mass_driver.migration import Migration
from mass_driver.model import PatchDriver

if sys.version_info < (3, 10):
    from importlib_metadata import EntryPoint, EntryPoints, entry_points
else:
    from importlib.metadata import EntryPoint, EntryPoints, entry_points


def discover_drivers() -> EntryPoints:
    """Discover all Drivers via plugin system"""
    return entry_points(group="massdriver.drivers")


def get_driver_entrypoint(driver_name: str) -> EntryPoint:
    """Fetch the given driver Entrypoint, by name"""
    drivers = discover_drivers()
    if driver_name not in drivers.names:
        raise ImportError(f"Driver '{driver_name}' not found in 'massdriver.drivers'")
    (driver,) = drivers.select(name=driver_name)
    return driver


def get_driver(driver_name: str) -> type[PatchDriver]:
    """Get the given driver Class, by entrypoint name"""
    driver = get_driver_entrypoint(driver_name)
    return driver.load()


def driver_from_config(config: Migration) -> PatchDriver:
    """Create PatchDriver instance from config file (TOML)"""
    driver_class = get_driver(config.driver)
    return driver_class.parse_obj(config.driver_config)
