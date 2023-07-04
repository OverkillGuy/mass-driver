"""A dummy source, returning the list of objects it was given"""

import csv
from pathlib import Path

from pydantic import FilePath

from mass_driver.models.repository import IndexedRepos, Repo, RepoUrl, Source


class RepolistSource(Source):
    """A Source that just returns a pre-configured list of repositories"""

    repos: list[RepoUrl]
    """The configured list of repositories to use, as list of cloneable URL"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        return {url: Repo(clone_url=url, repo_id=url) for url in self.repos}


class RepoFilelistSource(Source):
    """A Source reads repo list from file"""

    repo_file: FilePath
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

    repo_file: FilePath
    """The path to the newline-delimited file that holds repo ids"""
    clone_url_template: str
    """The repo clone URL template string, ready to inject ID into. Must contain {id}"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        if not self.repo_file.is_file():
            raise ValueError(f"Path not a real file:  '{self.repo_file}'")
        id_list = self.repo_file.read_text().strip().split("\n")
        return {
            repo_id: Repo(
                clone_url=self.clone_url_template.format(id=repo_id), repo_id=repo_id
            )
            for repo_id in id_list
        }


class CSVFileSource(Source):
    """Source reading repos from CSV file, attaching to patch_data any extra fields"""

    csv_file: FilePath
    """The path to the CSV file that holds repos"""
    reader_args: dict = {}
    """Keyword-arguments to pass to csv.DictReader"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        if not self.csv_file.is_file():
            raise ValueError(f"Path not a real file:  '{self.repo_file}'")
        reader_args = self.reader_args if self.reader_args else {}
        out: IndexedRepos = {}
        with open(self.csv_file) as csv_file:
            reader = csv.DictReader(csv_file, **reader_args)
            for row in reader:
                # Grab all the Repo-matching fields off CSV row
                repo_fields = set(Repo.__fields__) - {"patch_data"}
                csv_repo_fields = {k: row[k] for k in repo_fields if k in row}
                # Anything NOT in Repo fields goes to patch_data = {fieldname:csv-value}
                csv_extra_fields = row.keys() - repo_fields
                csv_extra_dict = {k: row[k] for k in csv_extra_fields}
                repo_obj = Repo(**csv_repo_fields, patch_data=csv_extra_dict)
                repo_id = row["repo_id"]
                out[repo_id] = repo_obj
        return out
