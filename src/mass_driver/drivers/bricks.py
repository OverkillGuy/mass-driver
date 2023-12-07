"""Patterns of PatchDriver that are reusable"""

from logging import Logger
from pathlib import Path

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class SingleFileEditor(PatchDriver):
    """A PatchDriver that edits a single file

    Reads {py:attr}`target_file` and calls
    {py:meth}`process_file` with it string content, saving the file if
    process changes the file, or returns given {py:class}`PatchResult` if any.

    """

    target_file: str
    """The file to edit"""

    def process_file(self, file_contents: str) -> str | PatchResult:
        """Process the file, returning the new content or a PatchResult"""
        raise NotImplementedError("Derive this function yourself")

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Edit the target file"""
        target_fullpath = Path(repo.cloned_path) / self.target_file
        if not target_fullpath.is_file():
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details="Target file does not exist",
            )
        file_content_before = target_fullpath.read_text()
        try:
            process_output = self.process_file(file_content_before)
            if isinstance(process_output, PatchResult):
                return process_output
            # In case it's a string: use it as data to write out
            file_content_after = process_output
        except Exception as e:
            self.logger.exception(e)
            return PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Error processing single file, error was {e}",
            )
        if file_content_after == file_content_before:
            return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
        target_fullpath.write_text(file_content_after)
        return PatchResult(outcome=PatchOutcome.PATCHED_OK)


class GlobFileEditor(PatchDriver):
    """A PatchDriver that edits multiple files via Glob

    Reads {py:attr}`target_glob` and calls
    {py:meth}`process_file` with each string content, saving the file if
    process changes each file.

    The aggregated {py:class}`PatchResult`s are processed via
    {py:func}`process_outcomes`, see the {py:attr}`fail_on_any_error` parameter.
    """

    target_glob: str
    """The glob for files to edit, relative to project root"""
    fail_on_any_error: bool = True
    """Whether or not to declare failure on any PATCH_ERRROR, or assume any OK as good"""

    def process_file(self, filename, file_contents: str) -> str | PatchResult:
        """Process a file, returning the new content or a PatchResult"""
        raise NotImplementedError("Derive this function yourself")

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Edit the target file"""
        targets = sorted(Path(repo.cloned_path).glob(self.target_glob))
        self.logger.info(f"Found {len(targets)} files to edit")

        outcomes: dict[str, PatchResult] = {}
        for target_fullpath in targets:
            target_relpath = str(target_fullpath.relative_to(repo.cloned_path))
            file_content_before = target_fullpath.read_text()
            try:
                process_output = self.process_file(target_relpath, file_content_before)
                if isinstance(process_output, PatchResult):
                    outcomes[target_relpath] = process_output
                # In case it's a string: use it as data to write out
                file_content_after = process_output
            except Exception as e:
                self.logger.exception(e)
                outcomes[target_relpath] = PatchResult(
                    outcome=PatchOutcome.PATCH_ERROR,
                    details=f"Error processing single file, error was {e}",
                )
            if file_content_after == file_content_before:
                outcomes[target_relpath] = PatchResult(
                    outcome=PatchOutcome.ALREADY_PATCHED
                )
            target_fullpath.write_text(file_content_after)
            outcomes[target_relpath] = PatchResult(outcome=PatchOutcome.PATCHED_OK)
        return process_outcomes(
            outcomes, fail_on_any_error=self.fail_on_any_error, logger=self.logger
        )


def process_outcomes(
    outcomes: dict[str, PatchResult], fail_on_any_error: bool, logger: Logger
):
    """Forward a OK PatchResult if an OK happened on any file"""
    oks = [
        fname for fname, p in outcomes.items() if p.outcome == PatchOutcome.PATCHED_OK
    ]
    errors = [
        (fname, p)
        for fname, p in outcomes.items()
        if p.outcome == PatchOutcome.PATCH_ERROR
    ]
    num_errors = len(errors)

    # First: deal with fail_on_any_error
    if fail_on_any_error and any(errors):
        all_errors_str = "\n".join(
            [f"{fname}:{p.details}" for fname, p in errors if p is not None]
        )
        return PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details=f"{num_errors} errors occured. Error(s):\n{all_errors_str}",
        )
    # Then check if any OK to forward
    if any(oks):
        if any(errors):
            details = (
                f"Ignoring {len(errors)} error(s) due to {len(oks)} file(s) patched OK"
            )
        else:
            details = "No errors to report"
        return PatchResult(outcome=PatchOutcome.PATCHED_OK, details=details)
    # No OK, but not fail_on_error: check all of one type:
    all_already_patched = all(
        [
            True if p.outcome == PatchOutcome.ALREADY_PATCHED else False
            for f, p in outcomes.items()
        ]
    )
    if all_already_patched:
        logger.info("All files we already patched, forwarding that")
        return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
    all_not_apply = all(
        [
            True if p.outcome == PatchOutcome.PATCH_DOES_NOT_APPLY else False
            for f, p in outcomes.items()
        ]
    )
    if all_not_apply:
        logger.info("All files were of Patch does not apply, forwarding that")
        return PatchResult(outcome=PatchOutcome.PATCH_DOES_NOT_APPLY)

    # No OK, but not fail_on_error, not all of one type:
    logger.info(f"No OK result to forward, but {len(errors)} errors")
    return PatchResult(
        outcome=PatchOutcome.PATCH_ERROR,
        details=f"No OK result to forward, but {len(errors)} errors",
    )
