"""Sources of repos to migrate"""

from typing import Optional

from pydantic import BaseModel, BaseSettings, DirectoryPath

RepoID = str
"""A unique identifier for a repository to process"""

RepoUrl = str
"""A repo's clone URL, either git@github.com format or local filesystem path"""


class Repo(BaseModel):
    """A sourced git repository, along with any per-repo info for patching"""

    clone_url: RepoUrl
    """The 'git clone'-able URL"""
    repo_id: RepoID
    """A unique name for the repo, to identify it against others"""
    patch_data: dict = {}
    """Arbitrary data dict from source"""
    cloned_path: Optional[DirectoryPath] = None
    """The filesystem path to the git cloned repo"""


IndexedRepos = dict[RepoID, Repo]
"""A "list" of repositories, but indexed by repo ID (Repo.repo_id)"""


class Source(BaseSettings):
    """Base class for Sources of Repo, on which to apply patching or scan"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        raise NotImplementedError("Source base class can't discover, use derived")

    class Config:
        """Configuration of the Source class"""

        underscore_attrs_are_private = True
        """Ensure that _api is treated private"""
        env_prefix = "SOURCE_"
