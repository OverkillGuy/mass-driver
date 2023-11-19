"""Patterns of PatchDriver that are reusable"""

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class SingleFileEditor(PatchDriver):
    """A PatchDriver that edits a single file

    Reads {py:attr}`target_file` and calls
    {py:meth}`process_file` with it string content, saving the file if
    process changes the file.

    """

    target_file: str

    def process_file(self, file_contents: str) -> str:
        """Process the file, returning the new content"""
        raise NotImplementedError("Derive this function yourself")

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Edit the target file"""
        target_fullpath = repo.cloned_path / self.target_file
        if not target_fullpath.is_file():
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details="Target file does not exist",
            )
        file_content_before = target_fullpath.read_text()
        try:
            file_content_after = self.process_file(file_content_before)
        except Exception as e:
            self.logger.exception(e)
            return PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Error processing single file, error was {e}",
            )
        if file_content_after == file_content_before:
            return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
        target_fullpath.write_text(file_content_before)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
