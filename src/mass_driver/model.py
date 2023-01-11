"""The core classes for creating Patches across Repositories"""

from pathlib import Path

from pydantic import BaseModel


class PatchDriver(BaseModel):
    """Base class for creating patches over repositories"""

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """
        Apply the update to given (cloned) Git Repository.

        If dry_run is True, just detect if the changes are needed.
        If dry_run is False, actually mutate the given folder
        """
        raise NotImplementedError("PatchDriver base class can't run, use derived")


class Forge:
    """Base class for git Forges like Github"""

    def create_pr(self, forge_repo: str, repo_path: Path, branch: str, msg: str):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        raise NotImplementedError("Forge base class can't create PR, use derived")

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        raise NotImplementedError("Forge base class can't get PR, use derived")
