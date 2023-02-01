"""Githubas Forge. Using the github lib if available"""

from github import Github

from mass_driver.forge import BranchName, Forge


class GithubForge(Forge):
    """Github API wrapper, capable of creating/getting PRs"""

    api: Github
    """A handle on the auth-ed Github API"""

    def __init__(self, auth_token: str):
        """Instantiate the Github API, mostly for authing"""
        self.api = Github(auth_token)

    def create_pr(
        self,
        forge_repo: str,
        base_branch: BranchName,
        head_branch: BranchName,
        pr_title: str,
        pr_body: str,
        draft: bool,
    ):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        repo = self.api.get_repo(forge_repo)
        return repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=head_branch,
            base=base_branch,
            draft=draft,
        )

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        repo = self.api.get_repo(forge_repo)
        return repo.get_pull(int(pr_id))
