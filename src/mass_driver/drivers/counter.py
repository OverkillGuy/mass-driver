"""Simplest Patch Driver: increments a file counter"""

from dataclasses import dataclass
from pathlib import Path

from mass_driver.model import PatchDriver


@dataclass
class Counter(PatchDriver):
    """Increments a counter in a given file of repo, creating if non-existent"""

    target_count: int
    counter_file: Path

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Process the counter file"""
        counter_filepath_abs = repo / self.counter_file
        if not counter_filepath_abs.is_file():
            print("File not found: let's Patch!")
            return True
        counter_content = counter_filepath_abs.read_text().strip()
        if not counter_content.isdigit():
            print("File content isn't a number: Patch!")
            return True
        counter_number = int(counter_content)
        counter_is_different = counter_number != self.target_count
        print(
            f"Measured: {counter_number}, target: {self.target_count}. Different? {counter_is_different}"
        )
        if counter_is_different and not dry_run:
            counter_filepath_abs.write_text(str(self.target_count))
        return counter_is_different
