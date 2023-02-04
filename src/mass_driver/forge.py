"""Base definition of Forge, applying changes across git Repositories"""

from pydantic import BaseModel

BranchName = str
"""A git branch name, assumed to exist remotely on the Forge"""


class Forge(BaseModel):
    """Base class for git Forges like Github"""

    auth_token: str

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
