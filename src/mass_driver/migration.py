"""Migration definitions, as map of PatchDriver over Sequence of Repos"""

from pydantic import BaseModel
from tomlkit import loads

TOML_PROJECTKEY = "mass-driver"


class Migration(BaseModel):
    """The TOML config file describing a migration"""

    migration_name: str
    """The short name of the migration, <50char for summarizing"""
    commit_message: str
    """The git commit message body to use when committing the migration"""
    branch_name: str | None
    """The branch name, if any, to use when committing the PatchDriver"""
    driver: str
    """The plugin-name of the PatchDriver to use, via plugin discovery"""
    driver_config: dict
    """The (opaque) configuration of the PatchDriver. Validated once driver loaded"""


def load_migration(migration_config: str) -> Migration:
    """Load up a TOML config of a migration into memory"""
    migration_dict = loads(migration_config)
    if TOML_PROJECTKEY not in migration_dict:
        raise ValueError(
            "Config file given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return Migration.parse_obj(migration_dict[TOML_PROJECTKEY])
