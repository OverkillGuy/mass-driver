"""Migration definitions, as map of PatchDriver over Sequence of Repos"""

from pydantic import BaseModel
from tomlkit import loads

from mass_driver.discovery import get_driver, get_forge
from mass_driver.forge import BranchName, Forge
from mass_driver.patchdriver import PatchDriver

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


class ForgeFileBase(BaseModel):
    """The basis of a ForgeFile, regardless of it Forge is loaded or not"""

    base_branch: BranchName
    """The base branch from which to create PR from (e.g. master or main)"""
    head_branch: BranchName
    """The head branch from which to create PR from (e.g. bugfix1)"""
    draft_pr: bool
    """Is the PR to be created a Draft?"""
    pr_title: str
    """The title of the PR to create"""
    pr_body: str
    """The body of the PR to create (multiline)"""


class ForgeFilePreload(ForgeFileBase):
    """The config file describing a forge, before we load the Forge class"""

    forge: str
    """The name of the forge to create PRs with, as plugin name"""


class ForgeFile(ForgeFileBase):
    """The config file describing a forge, before we load the Forge class"""

    forge: Forge
    """The instantiated forge to create PRs with"""

    @classmethod
    def from_config(cls, config_toml: str, auth_token: str):
        """Get a loaded forge from config contents"""
        config_noforge = load_forge_toml(config_toml)
        return load_forge(config_noforge, auth_token)


def load_forge_toml(forge_config: str) -> ForgeFilePreload:
    """Load up a TOML config of a forge into memory"""
    forge_dict = loads(forge_config)
    if TOML_PROJECTKEY not in forge_dict:
        raise ValueError(
            "Config file given invalid: " f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return ForgeFilePreload.parse_obj(forge_dict[TOML_PROJECTKEY])


def forge_from_config(config: ForgeFilePreload, auth_token: str) -> Forge:
    """Create Forge instance from config file (TOML)"""
    forge_class = get_forge(config.forge)
    breakpoint()
    return forge_class(auth_token=auth_token)


def load_forge(config: str, auth_token: str) -> ForgeFile:
    """Look up driver and validate configuration (de-opaquify)"""
    forge = load_forge_toml(config)
    forge_obj = forge_from_config(forge, auth_token)
    return ForgeFile(
        forge=forge_obj,
        base_branch=forge.base_branch,
        head_branch=forge.head_branch,
        draft_pr=forge.draft_pr,
        pr_title=forge.pr_title,
        pr_body=forge.pr_body,
    )
