"""The status of a single Repo's processing"""


from enum import Enum
from pydantic import BaseModel

from mass_driver.models.repository import ClonedRepo, SourcedRepo
from mass_driver.models.patchdriver import PatchResult
from mass_driver.models.forge import PRResult

ScanResult = dict[str, dict]
"""The output of one or more scanner(s) on a single repo, indexed by scanner-name"""

class RepoStatus(str, Enum):
    """The status of a single Repository"""

    SOURCED = "SOURCED"
    """Untouched from sourcing"""
    CLONED = "CLONED"
    """Cloned and branch adjusted as needed"""
    SCANNED = "SCANNED"
    """Repo has been scanned"""
    PATCHED = "PATCHED"
    """Patch has been applied"""
    FORGED = "FORGED"
    """Necessary forge from Patch has been raised"""



class RepoOutcome(BaseModel):
    """A single repo's processing status"""

    repo_id: str
    """The Repo's identifier among this run. Unique-ish string"""
    status: RepoStatus
    """The status of the repo's processing"""
    source: SourcedRepo
    """The Repo's info from Source"""
    clone: ClonedRepo | None = None
    """The cloned repo's data if any"""
    scan: ScanResult | None = None
    """The result of a Scan, if any"""
    patch: PatchResult | None = None
    """The result of a Scan, if any"""
    forge: PRResult | None = None
    """The result of Forge, if any"""
