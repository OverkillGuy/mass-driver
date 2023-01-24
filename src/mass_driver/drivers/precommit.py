"""Pre-commit autoupdate as a Mass Driver"""

import subprocess
from pathlib import Path

from mass_driver.patchdriver import PatchDriver, PatchOutcome, PatchResult


class PrecommitAutoupdate(PatchDriver):
    """Run 'pre-commit autoupdate' in a repo"""

    def run(self, repo: Path) -> PatchResult:
        """Apply pre-commit autoupdates"""
        subprocess.run(["pre-commit", "autoupdate"], cwd=repo)
        return PatchResult(PatchOutcome.PATCHED_OK)
