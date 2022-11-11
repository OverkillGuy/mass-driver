"""The core classes for creating Patches across Repositories"""

from pathlib import Path


class PatchDriver:
    """Base class for creating patches over repositories"""

    def detect(self, repo_path: Path) -> bool:
        """
        Scan the given (cloned) Git Repository for patch-ablity.

        Return True if the repo is "non-compliant", needing a patch.
        """
        raise NotImplementedError("PatchDriver base class can't detect, use derived")

    def patch(self, repo_path: Path):
        """Mutate the given (cloned) repo to Patch it out"""
        raise NotImplementedError("PatchDriver base class can't patch, use derived")


class Forge:
    """Base class for git Forges like Github"""

    def create_pr(self, forge_repo: str, repo_path: Path, branch: str, msg: str):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        raise NotImplementedError("Forge base class can't create PR, use derived")

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        raise NotImplementedError("Forge base class can't get PR, use derived")
