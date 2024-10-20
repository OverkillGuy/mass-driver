"""Imprints ("stamps") a new file onto a repository"""

from pathlib import Path

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class Stamper(PatchDriver):
    """Creates a new file onto a repository, aka "Stamping

    Any missing folder will be created on the way.

    New file's ownership will be set after succesful write.
    """

    filepath_to_create: str
    file_contents: str
    file_ownership: str = "0664"
    """Unix file permissions for the new file"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Create the file on given repo, creating folder the way"""
        target_path_abs = repo.cloned_path / Path(self.filepath_to_create)
        # Create parent folders on the way
        target_path_abs.parent.mkdir(parents=True, exist_ok=True)
        if target_path_abs.is_file():
            return PatchResult(
                outcome=PatchOutcome.ALREADY_PATCHED, details="File exists already"
            )
        with open(target_path_abs, "w") as fd:
            fd.write(self.file_contents)
            # File end with EOL, enforce it
            if not self.file_contents.endswith("\n"):
                fd.write("\n")
        # Set file ownership (octal conversion)
        target_path_abs.chmod(int(self.file_ownership, 8))
        return PatchResult(outcome=PatchOutcome.PATCHED_OK, details="File created")
