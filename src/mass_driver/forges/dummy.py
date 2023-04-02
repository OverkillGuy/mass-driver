"""Dummy Forge, does not do anything meaningful"""

from mass_driver.models.forge import BranchName, Forge

DUMMY_PR_URL = "https://github.com/OverkillGuy/sphinx-needs-tests/pull/1"
"""A random but real PR to use as dummy value"""


class DummyForge(Forge):
    """Doesn't do anything"""

    PR_URL: str = DUMMY_PR_URL
    """The PR's URL, for ease of access in tests"""

    some_param_for_forgeconfig: str
    """A parameter to set via forgeconfig, for tests"""

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

    def get_pr(self, forge_repo: str, pr_id: str):
        """Get the PR by ID on forge_repo"""
        return DUMMY_PR_URL
