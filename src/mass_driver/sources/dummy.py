"""A dummy source, returning the list of objects it was given"""

from mass_driver.models.source import Repo, Source


class RepolistSource(Source):
    """A Source that just returns a pre-configured list of repositories"""

    repos: list[str]
    """The configured list of repositories to use, as list of cloneable URL"""

    def discover(self) -> list[Repo]:
        """Discover a list of repositories"""
        return [Repo(clone_url=url, repo_id=url) for url in self.repos]
