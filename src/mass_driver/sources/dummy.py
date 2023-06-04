"""A dummy source, returning the list of objects it was given"""

from pathlib import Path

from mass_driver.models.source import Repo, Source


class RepolistSource(Source):
    """A Source that just returns a pre-configured list of repositories"""

    repos: list[str]
    """The configured list of repositories to use, as list of cloneable URL"""

    def discover(self) -> list[Repo]:
        """Discover a list of repositories"""
        return [Repo(clone_url=url, repo_id=url) for url in self.repos]


class RepoFilelistSource(Source):
    """A Source reads repo list from file"""

    repo_file: str
    """The path to the file that holds repos to read"""

    def discover(self) -> list[Repo]:
        """Discover a list of repositories"""
        repo_file_path = Path(self.repo_file)
        if not repo_file_path.is_file():
            raise ValueError(f"Repo-file path not a real file:  '{self.repo_file}'")
        repo_list = repo_file_path.read_text().strip().split("\n")
        return [Repo(clone_url=url, repo_id=url) for url in repo_list]
