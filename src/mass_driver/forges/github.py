"""Githubas Forge. Using the github lib if available"""

from pathlib import Path

try:
    from github import Github

    # We want to hard fail only when actively USING the dependencies, not just importing
    # it at toplevel (not actively using) ==> Set a flag for availability of deps,
    # to check at runtime and raise only then
    DEPS_AVAILABLE = True
except ImportError:
    Github = None  # Define a dummy type to avoid crash
    DEPS_AVAILABLE = False


from mass_driver.model import Forge


class GithubForge(Forge):
    """Increments a counter in a given file of repo, creating if non-existent"""

    api: Github
    """A handle on the auth-ed Github API"""

    def __init__(self, auth_token: str):
        """Instantiate the Github API, mostly for authing"""
        if not DEPS_AVAILABLE:
            raise ImportError(
                "Missing dependencies required for this Forge. "
                "Please install the package fully"
            )

        self.api = Github(auth_token)

    def create_pr(self, forge_repo: str, repo_path: Path, branch: str, msg: str):
        """Send a PR, with msg body, to forge_repo for given branch of repo_path"""
        raise NotImplementedError("Forge base class can't create PR, use derived")

    def get_pr(self, forge_repo: str, pr_id: str):
        """Send a PR with msg on upstream of repo at repo_path, for given branch"""
        repo = self.api.get_repo(forge_repo)
        return repo.get_pull(pr_id)
