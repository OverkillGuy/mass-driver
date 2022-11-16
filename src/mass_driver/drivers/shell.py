"""Generic shell command driver"""


import subprocess
from dataclasses import dataclass
from pathlib import Path

from mass_driver.model import PatchDriver


@dataclass
class ShellDriver(PatchDriver):
    """
    Run a generic shell command

    For instance, the following is a valid "sed" invocation:

    .. code:: python

        ShellDriver(command=["sed", "-i", "s/v0.1.0/v0.2.0/g", "version.txt"])

    Note that the process is run inside `subprocess.check_call` (raises CalledProcessError on bad
    exit code).
    """

    command: list[str]
    """Shell command to apply to the repository, as string list"""
    shell: bool = True
    """Passed to subprocess.check_call, to enable true shell behaviour rather than exec"""

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Run the command on the repo"""
        subprocess.check_call(self.command, cwd=repo, shell=self.shell)
        return True
