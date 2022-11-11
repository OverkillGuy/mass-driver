"""The core classes for creating Patches across Repositories"""

from pathlib import Path

GitUrl = str
"""A git-cloneable URL, HTTPS, GIT protocol or even local path"""


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
