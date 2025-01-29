"""Blindly deletes specific given files"""

from pathlib import Path

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class FileDeleter(PatchDriver):
    """Deletes files specified"""

    deletion_target: str | list[str]
    """The specific file or files to delete"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Apply file deletion"""
        target_files = self.deletion_target
        if isinstance(self.deletion_target, str):
            target_files = [self.deletion_target]
        files_deleted = []
        for file_to_delete in target_files:
            abs_to_delete = repo.cloned_path / Path(file_to_delete)
            if not abs_to_delete.is_file():
                continue
            abs_to_delete.unlink()
            files_deleted.append(file_to_delete)
        if not files_deleted:
            return PatchResult(outcome=PatchOutcome.PATCH_DOES_NOT_APPLY)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)
