"""Driver discovery system via plugins"""

import sys

from mass_driver.forge import Forge
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


def discover_forges() -> EntryPoints:
    """Discover all Forges via plugin system"""
    return entry_points(group=FORGE_ENTRYPOINT)


def get_forge_entrypoint(forge_name: str) -> EntryPoint:
    """Fetch the given forge Entrypoint, by name"""
    forges = discover_forges()
    if forge_name not in forges.names:
        raise ImportError(f"Forge '{forge_name}' not found in '{FORGE_ENTRYPOINT}'")
    (forge,) = forges.select(name=forge_name)
    return forge


def get_forge(forge_name: str) -> type[Forge]:
    """Get the given forge Class, by entrypoint name"""
    forge = get_forge_entrypoint(forge_name)
    return forge.load()
