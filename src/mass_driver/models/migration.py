"""Migration definitions, as map of PatchDriver over Sequence of Repos"""

from tomllib import loads

from pydantic import BaseModel

from mass_driver.discovery import get_driver, get_forge, get_source
from mass_driver.models.forge import BranchName, Forge
from mass_driver.models.patchdriver import PatchDriver
from mass_driver.models.repository import Source

TOML_PROJECTKEY = "mass-driver"


class MigrationFile(BaseModel):
    """The config file describing a migration, as transcribed before driver lookup"""

    commit_message: str
    """The git commit message body to use when committing the migration"""
    commit_author_name: str | None
    """Override the default (global) git commit author name"""
    commit_author_email: str | None
    """Override the default (global) git commit author email"""
    branch_name: str | None
    """The branch name, if any, to use when committing the PatchDriver"""
    driver_name: str
    """The plugin-name of the PatchDriver to use, via plugin discovery"""
    driver_config: dict
    """The (opaque) configuration of the PatchDriver. Validated once driver loaded"""


class MigrationLoaded(MigrationFile):
    """A Migration configuration, once the driver is loaded with its config"""

    driver: PatchDriver
    """Driver loaded (with validated configuration)"""

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
            "Migration Config file given invalid: "
            f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return MigrationFile.parse_obj(migration_dict[TOML_PROJECTKEY])


def driver_from_config(config: MigrationFile) -> PatchDriver:
    """Create PatchDriver instance from config file (TOML)"""
    driver_class = get_driver(config.driver_name)
    return driver_class.parse_obj(config.driver_config)


def load_driver(config: MigrationFile) -> MigrationLoaded:
    """Look up driver and validate configuration (de-opaquify)"""
    driver = driver_from_config(config)
    branch_name_override = (
        driver.__class__.__name__.lower()
        if config.branch_name is None
        else config.branch_name
    )
    migration = MigrationLoaded(driver=driver, **(config.dict()))
    migration.branch_name = branch_name_override
    return migration


class ForgeFile(BaseModel):
    """The config file describing a forge, before we load the Forge class"""

    base_branch: BranchName | None = None
    """The base branch from which to create PR from (e.g. master or main)"""
    head_branch: BranchName
    """The head branch from which to create PR from (e.g. bugfix1)"""
    git_push_first: bool = True
    """Do we need to push that branch before forging a PR?"""
    interactive_pause_every: int | None = None
    """How many forge action before pausing interactively, wait for OK (rate-limit)"""
    draft_pr: bool
    """Is the PR to be created a Draft?"""
    pr_title: str
    """The title of the PR to create"""
    pr_body: str
    """The body of the PR to create (multiline)"""
    forge_name: str
    """The name of the forge to create PRs with, as plugin name"""
    forge_config: dict = {}
    """Forge config vars. Overrides FORGE_ envvars: use for non-secrets"""


class ForgeLoaded(ForgeFile):
    """The config file describing a forge, once the Forge class is loaded"""

    forge: Forge
    """Forge loaded (with validated configuration)"""

    @classmethod
    def from_config(cls, config_toml: str):
        """Get a loaded forge from config contents"""
        config_noforge = load_forge_toml(config_toml)
        return load_forge(config_noforge)


def load_forge_toml(forge_config: str) -> ForgeFile:
    """Load up a TOML config of a forge into memory"""
    forge_dict = loads(forge_config)
    if TOML_PROJECTKEY not in forge_dict:
        raise ValueError(
            "Config file given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return ForgeFile.parse_obj(forge_dict[TOML_PROJECTKEY])


def forge_from_config(config: ForgeFile) -> ForgeLoaded:
    """Create Forge instance from config file (TOML)"""
    forge_class = get_forge(config.forge_name)
    forge_obj = forge_class(**config.forge_config)
    return ForgeLoaded(
        forge=forge_obj,
        **(config.dict()),
    )


def load_forge(config: str) -> ForgeLoaded:
    """Look up driver and validate configuration (de-opaquify)"""
    forge_file = load_forge_toml(config)
    return forge_from_config(forge_file)


class SourceConfigFile(BaseModel):
    """The config file describing a discovery event, as transcribed before Source lookup"""

    source_name: str
    """The plugin-name of the Source to use, via plugin discovery"""
    source_config: dict
    """The (opaque) configuration of the Source. Validated once source loaded"""


class SourceConfigLoaded(SourceConfigFile):
    """A Source configuration, once the Source is loaded with its config"""

    source: Source
    """Loaded Source (with validated configuration)"""

    @classmethod
    def from_config(cls, config_toml: str):
        """Get a loaded sourceconfig from config contents"""
        sourceconfig_nosource = load_sourceconfig(config_toml)
        return load_driver(sourceconfig_nosource)


def load_sourceconfig(source_config: str) -> SourceConfigFile:
    """Load up a TOML config of a migration into memory"""
    source_dict = loads(source_config)
    if TOML_PROJECTKEY not in source_dict:
        raise ValueError(
            "SourceConfig file given invalid: "
            f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return SourceConfigFile.parse_obj(source_dict[TOML_PROJECTKEY])


def source_from_config(config: SourceConfigFile) -> Source:
    """Create Source instance from config file (TOML)"""
    source_class = get_source(config.source_name)
    return source_class.parse_obj(config.source_config)


def load_source(config: SourceConfigFile) -> SourceConfigLoaded:
    """Look up source and validate configuration (de-opaquify)"""
    source = source_from_config(config)
    return SourceConfigLoaded(source=source, **(config.dict()))
