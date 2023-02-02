"""Githubas Forge. Using the github lib if available"""

from github import Github

from mass_driver.forge import BranchName, Forge


class GithubForge(Forge):
    """Github API wrapper, capable of creating/getting PRs"""

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
        api = Github(self.auth_token)
        repo = api.get_repo(repo_name)
        breakpoint()
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=head_branch,
            base=base_branch,
            draft=draft,
        )
        return pr.html_url

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        api = Github(self.auth_token)
        repo = api.get_repo(forge_repo)
        return repo.get_pull(int(pr_id))


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
