"""A dummy source, returning the list of objects it was given"""

from pathlib import Path

from mass_driver.models.source import IndexedRepos, Repo, RepoUrl, Source


class RepolistSource(Source):
    """A Source that just returns a pre-configured list of repositories"""

    repos: list[RepoUrl]
    """The configured list of repositories to use, as list of cloneable URL"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        return {url: Repo(clone_url=url, repo_id=url) for url in self.repos}


class RepoFilelistSource(Source):
    """A Source reads repo list from file"""

    repo_file: str
    """The path to the file that holds repos to read"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        repo_file_path = Path(self.repo_file)
        if not repo_file_path.is_file():
            raise ValueError(f"Repo-file path not a real file:  '{self.repo_file}'")
        repo_list = repo_file_path.read_text().strip().split("\n")
        return {url: Repo(clone_url=url, repo_id=url) for url in repo_list}


class TemplateFileSource(Source):
    """A Source that reads repo id from file, templating the clone URL around it"""

    repo_file: str
    """The path to the newline-delimited file that holds repo ids"""
    clone_url_template: str
    """The repo clone URL template string, ready to inject ID into. Must contain {id}"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        repo_file_path = Path(self.repo_file)
        if not repo_file_path.is_file():
            raise ValueError(f"Path not a real file:  '{self.repo_file}'")
        id_list = repo_file_path.read_text().strip().split("\n")
        return {
            repo_id: Repo(
                clone_url=self.clone_url_template.format(id=repo_id), repo_id=repo_id
            )
            for repo_id in id_list
        }
