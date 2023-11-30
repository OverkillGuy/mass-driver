"""The outcomes of activities"""

from pydantic import BaseModel

from mass_driver.models.forge import PRResult
from mass_driver.models.patchdriver import PatchResult
from mass_driver.models.repository import ClonedRepo, RepoID, SourcedRepo
from mass_driver.models.status import Error, Phase, ScanResult


class RepoOutcome(BaseModel):
    """A single repo's processing status"""

    repo_id: str
    """The Repo's identifier among this run. Unique-ish string"""
    status: Phase
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
    error: Error | None = None
    """The record of an error during a specific phase, if any happened"""


IndexedReposOutcome = dict[RepoID, RepoOutcome]
"""A set of RepoOutcome, indexed by RepoID"""
