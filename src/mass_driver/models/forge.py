"""Base definition of Forge, applying changes across git Repositories"""

from enum import Enum

from pydantic import BaseModel, BaseSettings

from mass_driver.models.repository import BranchName

PRStatus = dict[str, bool]
"""The status of a specific PR, as series of flags and bool-predicate.

Keys must be sorted (inserted) from most PR-completed (PR is merged/closed) to least
completed (unreviewed, draft, review-rejected, merge conflicts...)
"""


class Forge(BaseSettings):
    """Base class for git Forges like Github"""

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

    @property
    def pr_statuses(self) -> list[str]:
        """A list of possible PR statuses that will be returned by get_pr_status.

        List is sorted from most complete (accepted-and-merged) to least completed (not
        merged, not review-approved, has merge-conflicts).

        The returned list's ordering is used by the view-pr mass-driver command to show
        the PRs by status, from most completed to least completed.
        """
        raise NotImplementedError("Forge base class can't list PR status, use derived")

    class Config:
        """Configuration of the Forge class"""

        underscore_attrs_are_private = True
        """Ensure that _api is treated private"""
        env_prefix = "FORGE_"


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
    details: str | None = None
    """Details of the PR creation of this repo, if any"""
