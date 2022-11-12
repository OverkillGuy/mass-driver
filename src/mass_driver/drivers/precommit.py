"""Pre-commit autoupdate as a Mass Driver"""

import subprocess
from pathlib import Path

from mass_driver.model import PatchDriver


class PrecommitAutoupdate(PatchDriver):
    """Run 'pre-commit autoupdate' in a repo"""

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Apply pre-commit autoupdates"""
        if not dry_run:
            # Cannot detect without apply here
            return True
        subprocess.run(["pre-commit", "autoupdate"], cwd=repo)
        return True
