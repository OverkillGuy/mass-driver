"""PatchDriver base object definition"""

from enum import Enum

from pydantic import BaseModel

from mass_driver.models.repository import ClonedRepo


class PatchOutcome(str, Enum):
    """The category of result after using a PatchDriver over a single repository"""

    PATCHED_OK = "PATCHED_OK"
    """The Patch applied correctly"""
    ALREADY_PATCHED = "ALREADY_PATCHED"
    """The Patch was already applied, unnecessary to re-do"""
    PATCH_DOES_NOT_APPLY = "PATCH_DOES_NOT_APPLY"
    """The repo is missing a pre-requisite that makes patching irrelevant"""
    PATCH_ERROR = "PATCH_ERROR"
    """The Patch tried to apply, but failed somehow"""


class PatchResult(BaseModel):
    """The result of applying a patch on a repo"""

    outcome: PatchOutcome
    """The kind of result that patching had"""
    details: str | None = None
    """Details of the PatchDriver as it patched this repo, if any"""


class PatchDriver(BaseModel):
    """Base class for creating patches over repositories"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Apply the update to given (cloned) Git Repository.

        Return the outcome of patching for this repository.
        """
        raise NotImplementedError("PatchDriver base class can't run, use derived")
