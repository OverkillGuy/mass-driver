"""Driver discovery system via plugins"""

import sys

from mass_driver.patchdriver import PatchDriver

if sys.version_info < (3, 10):
    from importlib_metadata import EntryPoint, EntryPoints, entry_points
else:
    from importlib.metadata import EntryPoint, EntryPoints, entry_points

ENTRYPOINT = "massdriver"
"""The entrypoint we discover all types of plugins from"""
DRIVER_ENTRYPOINT = f"{ENTRYPOINT}.drivers"
"""The specific entrypoint for drivers discovery"""
FORGE_ENTRYPOINT = f"{ENTRYPOINT}.forges"
"""The specific entrypoint for Forge discovery"""


def discover_drivers() -> EntryPoints:
    """Discover all Drivers via plugin system"""
    return entry_points(group=DRIVER_ENTRYPOINT)


def get_driver_entrypoint(driver_name: str) -> EntryPoint:
    """Fetch the given driver Entrypoint, by name"""
    drivers = discover_drivers()
    if driver_name not in drivers.names:
        raise ImportError(f"Driver '{driver_name}' not found in '{DRIVER_ENTRYPOINT}'")
    (driver,) = drivers.select(name=driver_name)
    return driver


def get_driver(driver_name: str) -> type[PatchDriver]:
    """Get the given driver Class, by entrypoint name"""
    driver = get_driver_entrypoint(driver_name)
    return driver.load()
