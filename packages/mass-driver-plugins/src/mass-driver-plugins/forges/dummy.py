"""Dummy Forge, does not do anything meaningful"""

from pydantic import SecretStr

from mass_driver.models.forge import BranchName, Forge

DUMMY_PR_URL = "https://github.com/OverkillGuy/sphinx-needs-tests/pull/1"
"""A random but real PR to use as dummy value"""


class DummyForge(Forge):
    """Doesn't do anything"""

    PR_URL: str = DUMMY_PR_URL
    """The PR's URL, for ease of access in tests"""

    some_param_for_forgeconfig: SecretStr
    """A 'secret' parameter to set via forgeconfig, for tests. Type enforces no-leak!"""

    def create_pr(
        self,
        forge_repo_url: str,
        base_branch: BranchName,
        head_branch: BranchName,
        pr_title: str,
        pr_body: str,
        draft: bool,
    ):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        # Return-type of Forge not pinned down
        return DUMMY_PR_URL

    def get_pr_status(self, pr_url) -> str:
        """Get the PR by ID on forge_repo"""
        return "merged"

    @property
    def pr_statuses(self) -> list[str]:
        """List the possible PR status returned by get_pr_status, sorted by completion"""
        return ["merged", "open"]
