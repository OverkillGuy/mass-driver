"""Simplest Patch Driver: increments a file counter"""

from dataclasses import dataclass
from pathlib import Path

from mass_driver.patch_driver import PatchDriver


@dataclass
class Counter(PatchDriver):
    """Increments a counter in a given file of repo, creating if non-existent"""

    target_count: int
    counter_file: Path

    def detect(self, repo_path: Path) -> bool:
        """Detect if we need to patch the counter file"""
        counter_filepath_abs = repo_path / self.counter_file
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
        return counter_is_different

    def patch(self, repo_path: Path):
        """Increment the counter"""
        counter_filepath_abs = repo_path / self.counter_file
        counter_filepath_abs.write_text(str(self.target_count))
