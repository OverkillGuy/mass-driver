"""Sources of repos to migrate"""

from pydantic import BaseModel, BaseSettings


class Repo(BaseModel):
    """A sourced git repository, along with any per-repo info for patching"""

    clone_url: str
    """The 'git clone'-able URL"""
    repo_id: str
    """A unique name for the repo, to identify it against others"""
    patch_data: dict = {}
    """Arbitrary data dict from source"""


class Source(BaseSettings):
    """Base class for Sources of Repo, on which to apply patching or scan"""

    def discover(self) -> list[Repo]:
        """Discover a list of repositories"""
        raise NotImplementedError("Source base class can't discover, use derived")

    class Config:
        """Configuration of the Source class"""

        underscore_attrs_are_private = True
        """Ensure that _api is treated private"""
        env_prefix = "SOURCE_"
