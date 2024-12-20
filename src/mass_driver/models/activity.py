"""Activity, the top-level file format definition for `mass-driver run` command.

Encompasses both Migrations and Forge activities.
"""

from pydantic import BaseModel, ValidationError
from tomllib import loads

from mass_driver.discovery import get_scanner
from mass_driver.errors import ActivityLoadingException
from mass_driver.models.migration import (  # Forge,
    TOML_PROJECTKEY,
    ForgeFile,
    ForgeLoaded,
    MigrationFile,
    MigrationLoaded,
    SourceConfigFile,
    SourceConfigLoaded,
    forge_from_config,
    load_driver,
    load_source,
)
from mass_driver.models.outcome import IndexedReposOutcome
from mass_driver.models.scan import ScanFile, ScanLoaded, Scanner


class ActivityFile(BaseModel):
    """Top-level object for migration + forge, proxy for TOML file, pre-class-load"""

    source: SourceConfigFile | None = None
    scan: ScanFile | None = None
    migration: MigrationFile | None = None
    forge: ForgeFile | None = None


class ActivityLoaded(BaseModel):
    """Top-level object for migration + forge, proxy for TOML file, post-load"""

    source: SourceConfigLoaded | None = None
    scan: ScanLoaded | None = None
    migration: MigrationLoaded | None = None
    forge: ForgeLoaded | None = None

    @classmethod
    def from_config(cls, config_toml: str):
        """Get a loaded migration from config contents"""
        activity_file = load_activity_toml(config_toml)
        return load_activity(activity_file)


class ActivityOutcome(BaseModel):
    """The outcome of running activities"""

    repos: IndexedReposOutcome
    """The individual repos and their status"""


def load_activity_toml(activity_config: str) -> ActivityFile:
    """Load up a TOML config of activity into memory"""
    activity_dict = loads(activity_config)
    if TOML_PROJECTKEY not in activity_dict:
        raise ValueError(
            "Activity Config given invalid: "
            f"Missing top-level '{TOML_PROJECTKEY}' key"
        )
    return ActivityFile.parse_obj(activity_dict[TOML_PROJECTKEY])


def load_activity(activity: ActivityFile) -> ActivityLoaded:
    """Load up all plugins of an Activity

    Raises:
        ActivityLoadingException: Failure to load the full activity, like missing
          forge/source/patchdriver config, possibly via envvar

    """
    errors = []
    if activity.source is not None:
        try:
            source_loaded = load_source(activity.source)
        except ValidationError as e:
            errors.extend(bad_activity_error(e, "Source"))
    if activity.scan is not None:
        try:
            scan_loaded = load_scan(activity.scan)
        except ValidationError as e:
            errors.extend(bad_activity_error(e, "Scan", uses_envvars=False))
    if activity.migration is not None:
        try:
            migration_loaded = load_driver(activity.migration)
        except ValidationError as e:
            errors.extend(bad_activity_error(e, "PatchDriver", uses_envvars=False))
    if activity.forge is not None:
        try:
            forge_loaded = forge_from_config(activity.forge)
        except ValidationError as e:
            errors.extend(bad_activity_error(e, "Forge"))
    if errors:
        raise ActivityLoadingException(errors)
    return ActivityLoaded(
        source=source_loaded if activity.source is not None else None,
        scan=scan_loaded if activity.scan is not None else None,
        migration=migration_loaded if activity.migration is not None else None,
        forge=forge_loaded if activity.forge is not None else None,
    )


def bad_activity_error(
    e: ValidationError, object_name: str, uses_envvars: bool = True
) -> list[str]:
    """Deal with a loading/validation error of sub-activities"""
    env_prefix = object_name.upper() + "_"
    out = []
    for error in e.errors():
        if error["type"] == "missing" and uses_envvars:
            envvars = [env_prefix + var.upper() for var in error["loc"]]
            out.append(
                f"Missing {object_name} config: Set envvar(s) {', '.join(envvars)}"
            )
        else:
            out.append(f"{object_name} config validation error: {error}")
    return out


def load_scan(s: ScanFile):
    """Load the ScanFile, discovering drivers"""
    selected_scanners: list[Scanner] = []
    for selected_name in s.scanner_names:
        try:
            selected_scanner = get_scanner(selected_name)
            selected_scanners.append(selected_scanner)
        except ImportError as e:
            # Fail on the FIRST scanner load failure
            raise ImportError(
                "Failed to discover a scanner from given scanner list"
            ) from e
    return ScanLoaded(scanner_names=s.scanner_names, scanners=selected_scanners)
