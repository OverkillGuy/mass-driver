"""Imprints ("stamps") a new file onto a repository"""

from pathlib import Path

from mass_driver.patchdriver import PatchDriver, PatchOutcome, PatchResult


class Stamper(PatchDriver):
    """Creates a new file onto a repository, aka "Stamping"""

    filepath_to_create: str
    file_contents: str

    def run(self, repo: Path) -> PatchResult:
        """Create the file on given repo"""
        target_path_abs = repo / Path(self.filepath_to_create)
        if target_path_abs.is_file():
            return PatchResult(
                outcome=PatchOutcome.ALREADY_PATCHED, details="File exists already"
            )
        with open(target_path_abs, "w") as fd:
            fd.write(self.file_contents)
            # File end with EOL, enforce it
            if not self.file_contents.endswith("\n"):
                fd.write("\n")
        return PatchResult(outcome=PatchOutcome.PATCHED_OK, details="File created")
