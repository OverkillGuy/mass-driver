"""Generic shell command driver"""

import subprocess

from mass_driver.models.patchdriver import PatchDriver, PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo


class ShellDriver(PatchDriver):
    """Run a generic shell command

    For instance, the following is a valid "sed" invocation:

    ```python
    ShellDriver(command=["sed", "-i", "s/v0.1.0/v0.2.0/g", "version.txt"])
    ```

    Note that the process is run inside {py:func}`subprocess.check_call` (raises CalledProcessError on bad
    exit code).
    """

    command: list[str]
    """Shell command to apply to the repository, as string list"""
    shell: bool = True
    """Passed to subprocess.run, to enable true shell behaviour rather than exec"""

    def run(self, repo: ClonedRepo) -> PatchResult:
        """Run the command on the repo"""
        cmd = subprocess.run(
            self.command,
            cwd=repo.cloned_path,
            shell=self.shell,
            capture_output=True,
        )
        if cmd.stdout.strip():
            self.logger.info(cmd.stdout)
        if cmd.stderr.strip():
            self.logger.error(cmd.stderr)
        return (
            PatchResult(outcome=PatchOutcome.PATCHED_OK)
            if cmd.returncode == 0
            else PatchResult(outcome=PatchOutcome.PATCH_ERROR, details=cmd.stderr)
        )
