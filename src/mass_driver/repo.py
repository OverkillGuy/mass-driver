"""Cloning remote repos (repos not using local path)"""

from pathlib import Path

from git import Repo

from mass_driver.patch_driver import PatchDriver

DEFAULT_CACHE = Path(".mass_driver/repos/")


def clone_if_remote(repo_path: str, cache_folder: Path = DEFAULT_CACHE) -> Repo:
    """Build a git Repo; If repo_path isn't a directory, clone it"""
    if Path(repo_path).is_dir():
        return Repo(path=repo_path)
    if Repo(repo_path).workding_dir:
        return Repo(repo_path)
    *_junk, repo_blurb = repo_path.split(":")
    org, repo_name = repo_blurb.split("/")
    cloned = Repo().clone_from(
        url=repo_path,
        to_path=cache_folder / org / repo_name,
        multi_options=["--depth=1"],
    )
    return cloned


def commit(repo: Repo, driver: PatchDriver):
    """Commit the repo's changes, given the PatchDriver that did it"""
    assert repo.is_dirty(untracked_files=True), "Repo is clean, nothing to commit"
    repo.git.add(A=True)
    repo.git.commit(m="Bump by driver")
