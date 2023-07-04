"""Activity, the top-level file format definition for `mass-driver run` command.

Encompasses both Migrations and Forge activities.
"""

from tomllib import loads

from pydantic import BaseModel

from mass_driver.discovery import get_scanners
from mass_driver.models.forge import PRResult
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
from mass_driver.models.patchdriver import PatchResult
from mass_driver.models.repository import IndexedClonedRepos, IndexedRepos, RepoID
from mass_driver.models.scan import ScanFile, ScanLoaded, Scanner

IndexedPatchResult = dict[RepoID, PatchResult]
"""A set of PatchResults, indexed by original repo URL given as input"""

IndexedPRResult = dict[RepoID, PRResult]
"""A set of PRResults, indexed by original repo URL given as input"""

ScanResult = dict[str, dict]
"""The output of one or more scanner(s) on a single repo, indexed by scanner-name"""

IndexedScanResult = dict[RepoID, ScanResult]
"""A set of results of N scanners over multiple repos, indexed by original repo URL"""


class ActivityFile(BaseModel):
    """Top-level object for migration + forge, proxy for TOML file, pre-class-load"""

    source: SourceConfigFile | None = None
    scan: ScanFile | None = None
    migration: MigrationFile | None = None
    forge: ForgeFile | None = None
    # TODO: Add RepoSource here


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

    repos_sourced: IndexedRepos = {}
    """The repos, as discovered from Source"""
    repos_cloned: IndexedClonedRepos = {}
    """The repos, as cloned"""
    scan_result: IndexedScanResult | None = None
    """A lookup table of the scan results, indexed by repos_input url"""
    migration_result: IndexedPatchResult | None = None
    """A lookup table of the results of a Migration, indexed by repos_input url"""
    forge_result: IndexedPRResult | None = None
    """A lookup table of the results of a Forge, indexed by repos_input url"""


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
    """Load up all plugins of an Activity"""
    if activity.source is not None:
        source_loaded = load_source(activity.source)
    if activity.scan is not None:
        scan_loaded = load_scan(activity.scan)
    if activity.migration is not None:
        migration_loaded = load_driver(activity.migration)
    if activity.forge is not None:
        forge_loaded = forge_from_config(activity.forge)
    return ActivityLoaded(
        source=source_loaded if activity.source is not None else None,
        scan=scan_loaded if activity.scan is not None else None,
        migration=migration_loaded if activity.migration is not None else None,
        forge=forge_loaded if activity.forge is not None else None,
    )


def load_scan(s: ScanFile):
    """Load the ScanFile, discovering drivers"""
    all_scanners = get_scanners()
    scanners_by_name = {scanner.name: scanner for scanner in all_scanners}
    selected_scanners: list[Scanner] = []
    for selected_name in s.scanner_names:
        if selected_name in scanners_by_name:
            selected_scanners.append(scanners_by_name[selected_name])
    return ScanLoaded(scanner_names=s.scanner_names, scanners=selected_scanners)
