"""Activity, the top-level file format definition for `mass-driver run` command.

Encompasses both Migrations and Forge activities.
"""

from pathlib import Path
from tomllib import loads

from pydantic import BaseModel

from mass_driver.models.forge import PRResult
from mass_driver.models.migration import (  # Forge,
    TOML_PROJECTKEY,
    ForgeFile,
    ForgeLoaded,
    MigrationFile,
    MigrationLoaded,
    forge_from_config,
    load_driver,
)
from mass_driver.models.patchdriver import PatchResult

RepoUrl = str
"""A repo's clone URL, either git@github.com format or local filesystem path"""

IndexedPatchResult = dict[RepoUrl, PatchResult]
"""A set of PatchResults, indexed by original repo URL given as input"""

IndexedPRResult = dict[RepoUrl, PRResult]
"""A set of PRResults, indexed by original repo URL given as input"""

RepoPathLookup = dict[RepoUrl, Path]
"""A lookup table for the local cloned repo path, given its remote equivalent (or filesystem path)"""


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
    def from_config(cls, config_toml: str):
        """Get a loaded migration from config contents"""
        activity_file = load_activity_toml(config_toml)
        return load_activity(activity_file)


class ActivityOutcome(BaseModel):
    """The outcome of running activities"""

    repos_input: list[RepoUrl]
    """The initial input we were iterating over"""
    local_repos_path: RepoPathLookup
    """A lookup table for the on-disk cloned filepath of each repo, indexed by repos_input url"""
    migration_result: IndexedPatchResult | None = None
    """A lookup table of the results of a Migration, indexed by repos_input url"""
    forge_result: IndexedPRResult | None = None
    """A lookup table of the results of a Forge, indexed by repos_input url"""


def load_activity_toml(migration_config: str) -> ActivityFile:
    """Load up a TOML config of activity into memory"""
    migration_dict = loads(migration_config)
    if TOML_PROJECTKEY not in migration_dict:
        raise ValueError(
            "Config given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return ActivityFile.parse_obj(migration_dict[TOML_PROJECTKEY])


def load_activity(activity: ActivityFile) -> ActivityLoaded:
    """Load up all plugins of an Activity"""
    if activity.migration is not None:
        migration_loaded = load_driver(activity.migration)
    if activity.forge is not None:
        forge_loaded = forge_from_config(activity.forge)
    return ActivityLoaded(
        migration=migration_loaded if activity.migration is not None else None,
        forge=forge_loaded if activity.forge is not None else None,
    )
