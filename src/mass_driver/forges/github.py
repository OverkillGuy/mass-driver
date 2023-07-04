"""Githubas Forge. Using the github lib if available"""

from github import AppAuthentication, Github
from pydantic import SecretStr

from mass_driver.models.forge import BranchName, Forge


class GithubBaseForge(Forge):
    """Base for github forge"""

    _github_api: Github

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
        repo_name = detect_github_repo(forge_repo_url)
        repo = self._github_api.get_repo(repo_name)
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=head_branch,
            base=base_branch,
            draft=draft,
        )
        return pr.html_url

    def get_pr(self, forge_repo: str, pr_id: str):
        """Get the PR by ID on forge_repo"""
        repo = self._github_api.get_repo(forge_repo)
        return repo.get_pull(int(pr_id))


class GithubPersonalForge(GithubBaseForge):
    """Github API wrapper for personal user token use, capable of creating/getting PRs

    Reliance on pygithub means only able to deliver personal user token PRs, no
    Github app authentication.
    """

    token: SecretStr
    """Github personal access token"""

    def __init__(self, **data):
        """Log in to Github first"""
        super().__init__(**data)
        self._github_api = Github(login_or_token=self.token.get_secret_value())


class GithubAppForge(GithubBaseForge):
    """Create PRs on Github as a Github App, not user"""

    app_id: SecretStr
    app_private_key: SecretStr
    app_installation_id: int

    def __init__(self, **data):
        """Log in to Github first"""
        super().__init__(**data)
        auth = AppAuthentication(
            app_id=self.app_id.get_secret_value(),
            private_key=self.app_private_key.get_secret_value(),
            installation_id=self.app_installation_id.get_secret_value(),
        )
        self._github_api = Github(app_auth=auth)


# FIXME: Github App login blocked by "no such module JWT.encode"


def detect_github_repo(remote_url: str):
    """Find the github remote from a cloneable URL

    >>> detect_github_repo("git@github.com:OverkillGuy/sphinx-needs-test.git")
    'OverkillGuy/sphinx-needs-test'
    """
    if ":" not in remote_url:
        raise ValueError(
            f"Given remote URL is not a valid Github clone URL: '{remote_url}'"
        )
    _junk, gh_name = remote_url.split(":")
    return gh_name.removesuffix(".git")
