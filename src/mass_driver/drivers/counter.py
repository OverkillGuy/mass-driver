"""Dummy Patch Driver: increments a file counter

Simplest code we could implement that demonstrates PatchDriver capabilities.
"""

from mass_driver.drivers.bricks import SingleFileEditor
from mass_driver.models.patchdriver import PatchOutcome, PatchResult


class Counter(SingleFileEditor):
    """Increments a counter in a given file of repo, creating if non-existent"""

    target_count: int

    def process_file(self, file_contents: str) -> str | PatchResult:
        """Process the counter"""
        stripped_content = file_contents.strip()
        if not stripped_content.isdigit():
            return PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details="Counter file isn't an integer",
            )
        counter_number = int(stripped_content)
        if counter_number == self.target_count:
            return PatchResult(outcome=PatchOutcome.ALREADY_PATCHED)
        return str(self.target_count) + "\n"  # UNIX files valid iff has newline EOF
