"""Driver discovery system via plugins"""

from importlib.metadata import EntryPoint, EntryPoints, entry_points
from typing import Callable

from mass_driver.models.forge import Forge
from mass_driver.models.patchdriver import PatchDriver
from mass_driver.models.repository import Source
from mass_driver.models.scan import Scanner

ENTRYPOINT = "massdriver"
"""The entrypoint we discover all types of plugins from"""
DRIVER_ENTRYPOINT = f"{ENTRYPOINT}.drivers"
"""The specific entrypoint for drivers discovery"""
FORGE_ENTRYPOINT = f"{ENTRYPOINT}.forges"
"""The specific entrypoint for Forge discovery"""
SCANNER_ENTRYPOINT = f"{ENTRYPOINT}.scanners"
"""The specific entrypoint for Scanner discovery"""
SOURCE_ENTRYPOINT = f"{ENTRYPOINT}.sources"
"""The specific entrypoint for Source discovery"""


def discover_drivers() -> EntryPoints:
    """Discover all Drivers via plugin system"""
    return entry_points(group=DRIVER_ENTRYPOINT)


def discover_forges() -> EntryPoints:
    """Discover all Forges via plugin system"""
    return entry_points(group=FORGE_ENTRYPOINT)


def discover_sources() -> EntryPoints:
    """Discover all Sources via plugin system"""
    return entry_points(group=SOURCE_ENTRYPOINT)


def get_plugin_entrypoint(
    plugin: str, name: str, entrypoint: str, discover: Callable
) -> EntryPoint:
    """Fetch the given plugin's Entrypoint, by name"""
    plugin_objs = discover()
    if name not in plugin_objs.names:
        raise ImportError(f"{plugin} '{name}' not found in '{entrypoint}'")
    (plugin_obj,) = plugin_objs.select(name=name)
    return plugin_obj


def get_driver_entrypoint(driver_name: str) -> EntryPoint:
    """Fetch the given driver Entrypoint, by name"""
    return get_plugin_entrypoint(
        "driver", driver_name, DRIVER_ENTRYPOINT, discover_drivers
    )


def get_forge_entrypoint(forge_name: str) -> EntryPoint:
    """Fetch the given forge Entrypoint, by name"""
    return get_plugin_entrypoint("forge", forge_name, FORGE_ENTRYPOINT, discover_forges)


def get_source_entrypoint(source_name: str) -> EntryPoint:
    """Fetch the given source Entrypoint, by name"""
    return get_plugin_entrypoint(
        "source", source_name, SOURCE_ENTRYPOINT, discover_sources
    )


def get_driver(driver_name: str) -> type[PatchDriver]:
    """Get the given driver Class, by entrypoint name"""
    return get_driver_entrypoint(driver_name).load()


def get_forge(forge_name: str) -> type[Forge]:
    """Get the given forge Class, by entrypoint name"""
    return get_forge_entrypoint(forge_name).load()


def get_source(source_name: str) -> type[Source]:
    """Get the given source Class, by entrypoint name"""
    return get_source_entrypoint(source_name).load()


def get_scanners() -> list[Scanner]:
    """Grab all discovered scanners"""
    scanners = entry_points(group=SCANNER_ENTRYPOINT)
    return [Scanner(name=s.name, func=s.load()) for s in scanners]
