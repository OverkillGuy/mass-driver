"""Migration definitions, as map of PatchDriver over Sequence of Repos"""

from pydantic import BaseModel
from tomlkit import loads

from mass_driver.discovery import get_driver
from mass_driver.model import PatchDriver

TOML_PROJECTKEY = "mass-driver"


class MigrationBase(BaseModel):
    """The shared base for Migration config object, regardless of if driver is loaded"""

    migration_name: str
    """The short name of the migration, <50char for summarizing"""
    commit_message: str
    """The git commit message body to use when committing the migration"""


class MigrationFile(MigrationBase):
    """The config file describing a migration, as transcribed before driver lookup"""

    branch_name: str | None
    """The branch name, if any, to use when committing the PatchDriver"""
    driver: str
    """The plugin-name of the PatchDriver to use, via plugin discovery"""
    driver_config: dict
    """The (opaque) configuration of the PatchDriver. Validated once driver loaded"""


class Migration(MigrationBase):
    """A Migration configuration, once the driver is loaded with its config"""

    branch_name: str
    """The branch name for committing the PatchDriver's action. Defaults to drivername"""
    driver: PatchDriver
    """Driver with its validated configuration in place"""

    @classmethod
    def from_config(cls, config_toml: str):
        """Get a loaded migration from config contents"""
        migration_nodriver = load_migration(config_toml)
        return load_driver(migration_nodriver)


def load_migration(migration_config: str) -> MigrationFile:
    """Load up a TOML config of a migration into memory"""
    migration_dict = loads(migration_config)
    if TOML_PROJECTKEY not in migration_dict:
        raise ValueError(
            "Config file given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return MigrationFile.parse_obj(migration_dict[TOML_PROJECTKEY])


def driver_from_config(config: MigrationFile) -> PatchDriver:
    """Create PatchDriver instance from config file (TOML)"""
    driver_class = get_driver(config.driver)
    return driver_class.parse_obj(config.driver_config)


def load_driver(config: MigrationFile) -> Migration:
    """Look up driver and validate configuration (de-opaquify)"""
    driver = driver_from_config(config)
    branch_name = (
        driver.__class__.__name__.lower()
        if config.branch_name is None
        else config.branch_name
    )
    return Migration(
        migration_name=config.migration_name,
        commit_message=config.commit_message,
        branch_name=branch_name,
        driver=driver,
    )
