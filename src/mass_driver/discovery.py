"""Driver discovery system via plugins"""

import sys

from tomlkit import loads

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


def driver_from_config(config_str: str) -> PatchDriver:
    """Create PatchDriver instance from config file (TOML)"""
    config = loads(config_str)
    print(config)
    # FIXME: No schema-ing yet.
    assert "driver" in config, "Config must have top-level 'driver' key"
    drivers = config["driver"]
    assert len(drivers) == 1, "Config key 'driver' must have ONE item"
    driver_name = list(drivers.keys())[0]  # First and only
    driver_config = drivers[driver_name]
    print(f"Driver: '{driver_name}'")
    print(f"Config: {driver_config}")
    driver_class = get_driver(driver_name)
    return driver_class(**driver_config)
