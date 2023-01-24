"""Simplest Patch Driver: increments a file counter"""

from pathlib import Path

from mass_driver.patchdriver import PatchDriver, PatchOutcome, PatchResult


class Counter(PatchDriver):
    """Increments a counter in a given file of repo, creating if non-existent"""

    target_count: int
    counter_file: str

    def run(self, repo: Path) -> PatchResult:
        """Process the counter file"""
        counter_filepath_abs = repo / self.counter_file
        if not counter_filepath_abs.is_file():
            return PatchResult(
                outcome=PatchOutcome.PATCH_DOES_NOT_APPLY,
                details="No counter file exists yet",
            )
        counter_content = counter_filepath_abs.read_text().strip()
        if not counter_content.isdigit():
            return PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details="Counter file isn't an integer",
            )
        counter_number = int(counter_content)
        counter_is_different = counter_number != self.target_count
        print(
            f"Measured: {counter_number}, target: {self.target_count}. Different? {counter_is_different}"
        )
        if counter_is_different:
            counter_filepath_abs.write_text(str(self.target_count))
            return PatchResult(outcome=PatchOutcome.PATCHED_OK)
        # COUNTER already same value
        return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
