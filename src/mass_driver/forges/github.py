"""Githubas Forge. Using the github lib if available"""

import re

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

    def get_pr_status(self, pr_url: str) -> str:
        """Get the status of a single given PR, used as key to group PRs by status"""
        owner, repo, pr_num = detect_pr_info(pr_url)
        owner_repo = f"{owner}/{repo}"
        pr_obj = self._get_pr(owner_repo, pr_num)
        if pr_obj.merged:
            return "merged"
        if pr_obj.state == "closed":
            return "closed (but not merged)"
        if pr_obj.mergeable:
            return "mergeable (no conflict)"
        return "non-mergeable (conflicts)"

    @property
    def pr_statuses(self) -> list[str]:
        """List possible PR statuses that will be returned by get_pr_status.

        List is sorted from most complete (accepted-and-merged) to least completed (not
        merged, not review-approved, has merge-conflicts).

        The returned list's ordering is used by the view-pr mass-driver command to show
        the PRs by status, from most completed to least completed.
        """
        return [
            "merged",
            "closed (but not merged)",
            "mergeable (no conflict)",
            "non-mergeable (conflicts)",
        ]

    def _get_pr(self, forge_repo: str, pr_id: str):
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


def detect_pr_info(pr_url: str) -> tuple[str, str, str]:
    """Detect a PR's repo and number

    >>> detect_pr_info("https://github.com/OverkillGuy/sphinx-needs-test/pull/1")
    ('OverkillGuy', 'sphinx-needs-test', '1')
    """
    GITHUB_PR_REGEX = re.compile(
        r"""https://github.com/([a-zA-Z0-9Z_\.-]+)/([a-zA-Z0-9_\.-]+)/pull/([0-9]+)"""
    )
    match = re.fullmatch(GITHUB_PR_REGEX, pr_url)
    if not match:
        raise ValueError(f"PR URL {pr_url} doesn't map to github PR regex")
    owner, repo, prnum = match.groups()
    return (owner, repo, prnum)
