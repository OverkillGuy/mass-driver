"""Dummy Patch Driver: increments a file counter

Simplest code we could implement that demonstrates PatchDriver capabilities.
"""


from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class Counter(PatchDriver):
    """Increments a counter in a given file of repo, creating if non-existent"""

    target_count: int
    counter_file: str

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Process the counter file"""
        counter_filepath_abs = repo.cloned_path / self.counter_file
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
            counter_filepath_abs.write_text(str(self.target_count) + "\n")
            return PatchResult(outcome=PatchOutcome.PATCHED_OK)
        # COUNTER already same value
        return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
