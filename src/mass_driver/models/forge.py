"""Base definition of Forge, applying changes across git Repositories"""

from enum import Enum

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from mass_driver.models.repository import BranchName
from mass_driver.models.status import Error

PRStatus = dict[str, bool]
"""The status of a specific PR, as series of flags and bool-predicate.

Keys must be sorted (inserted) from most PR-completed (PR is merged/closed) to least
completed (unreviewed, draft, review-rejected, merge conflicts...)
"""


class Forge(BaseSettings):
    """Base class for git Forges like Github"""

    model_config = SettingsConfigDict(env_prefix="FORGE_")

    def create_pr(
        self,
        forge_repo_url: str,
        base_branch: BranchName,
        head_branch: BranchName,
        pr_title: str,
        pr_body: str,
        draft: bool,
    ) -> str:
        """Send a PR to forge_repo for given branch of repo_path. Returns PR HTML URL"""
        raise NotImplementedError("Forge base class can't create PR, use derived")

    def get_pr_status(self, pr: str) -> str:
        """Get the status of a single given PR, used as key to group PRs by status"""
        raise NotImplementedError("Forge base class can't get PR status, use derived")


class PROutcome(str, Enum):
    """The category of result after using a Forge over a single repository"""

    PR_CREATED = "PR_CREATED"
    """The PR was created correctly"""
    PR_FAILED = "PR_FAILED"
    """The PR failed to be created"""


class PRResult(BaseModel):
    """The result of applying a patch on a repo"""

    outcome: PROutcome
    """The kind of result that PR creation had"""
    pr_html_url: str | None = None
    """The HTML URL of the PR that was generated, if any"""
    error: Error | None = None
    """Detail of the error, that applied during patching, if any"""
