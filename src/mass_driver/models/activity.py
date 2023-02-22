"""Activity, the top-level file format definition for `mass-driver run` command.

Encompasses both Migrations and Forge activities.
"""

from tomllib import loads

from pydantic import BaseModel

from mass_driver.models.migration import (  # Forge,
    TOML_PROJECTKEY,
    ForgeFile,
    ForgeLoaded,
    MigrationFile,
    MigrationLoaded,
    forge_from_config,
    load_driver,
)


class ActivityFile(BaseModel):
    """Top-level object for migration + forge, proxy for TOML file, pre-class-load"""

    migration: MigrationFile | None = None
    forge: ForgeFile | None = None
    # TODO: Add RepoSource here


class ActivityLoaded(BaseModel):
    """Top-level object for migration + forge, proxy for TOML file, post-load"""

    migration: MigrationLoaded | None = None
    forge: ForgeLoaded | None = None

    @classmethod
    def from_config(cls, config_toml: str, auth_token: str | None):
        """Get a loaded migration from config contents"""
        activity_file = load_activity_toml(config_toml)
        return load_activity(activity_file, auth_token)


def load_activity_toml(migration_config: str) -> ActivityFile:
    """Load up a TOML config of activity into memory"""
    migration_dict = loads(migration_config)
    if TOML_PROJECTKEY not in migration_dict:
        raise ValueError(
            "Config given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return ActivityFile.parse_obj(migration_dict[TOML_PROJECTKEY])


def load_activity(activity: ActivityFile, auth_token: str | None) -> ActivityLoaded:
    """Load up all plugins of an Activity"""
    if activity.migration is not None:
        migration_loaded = load_driver(activity.migration)
    if activity.forge is not None:
        if auth_token is None:
            raise ValueError("Missing auth token")
        forge_loaded = forge_from_config(activity.forge, auth_token)
    return ActivityLoaded(
        migration=migration_loaded if activity.migration is not None else None,
        forge=forge_loaded if activity.forge is not None else None,
    )
