"""Base definition of Forge, applying changes across git Repositories"""

from enum import Enum

from pydantic import BaseModel, BaseSettings

BranchName = str
"""A git branch name, assumed to exist remotely on the Forge"""


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
    ):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        pass

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        raise NotImplementedError("Forge base class can't get PR, use derived")

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
