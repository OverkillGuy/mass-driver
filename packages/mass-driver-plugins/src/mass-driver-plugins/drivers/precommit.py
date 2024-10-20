"""Pre-commit autoupdate as a Mass Driver"""

import subprocess

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class PrecommitAutoupdate(PatchDriver):
    """Run 'pre-commit autoupdate' in a repo"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Apply pre-commit autoupdates"""
        subprocess.run(["pre-commit", "autoupdate"], cwd=repo.cloned_path)
        return PatchResult(PatchOutcome.PATCHED_OK)
