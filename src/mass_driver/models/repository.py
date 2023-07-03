"""Repositories for cloning and patching"""

from pydantic import BaseModel, BaseSettings, DirectoryPath

BranchName = str
"""A git branch name, assumed to exist remotely on the Forge"""


RepoID = str
"""A unique identifier for a repository to process"""

RepoUrl = str
"""A repo's clone URL, either git@github.com format or local filesystem path"""


class Repo(BaseModel):
    """A repository as-discovered, pre-cloning, along with any Sourced metadata"""

    clone_url: RepoUrl
    """The 'git clone'-able URL"""
    repo_id: RepoID
    """A unique name for the repo, to identify it against others"""
    upstream_branch: BranchName | None = None
    """A git branch to check out fro mremote, if any (defaults to None = use as-is)"""
    force_pull: bool = False
    """Pull the given branch before handing it over (useful when reusing repos)"""
    patch_data: dict = {}
    """Arbitrary data dict from Source"""


class ClonedRepo(Repo):
    """A repository after it has been successfully cloned, branch configured"""

    cloned_path: DirectoryPath
    """The filesystem path to the git cloned repo"""
    current_branch: BranchName
    """The name of the currently checked out branch"""


IndexedRepos = dict[RepoID, Repo]
"""A "list" of repositories, but indexed by repo ID (Repo.repo_id)"""

IndexedClonedRepos = dict[RepoID, ClonedRepo]
"""A "list" of cloned repositories, but indexed by repo ID (ClonedRepo.repo_id)"""


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
