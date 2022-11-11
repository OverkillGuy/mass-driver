"""Cloning remote repos (repos not using local path)"""

from pathlib import Path

from git import Repo

from mass_driver.model import PatchDriver

DEFAULT_CACHE = Path(".mass_driver/repos/")


def clone_if_remote(repo_path: str, cache_folder: Path = DEFAULT_CACHE) -> Repo:
    """Build a git Repo; If repo_path isn't a directory, clone it"""
    if Path(repo_path).is_dir():
        print("Given an existing (local) repo: no cloning")
        return Repo(path=repo_path)
    if ":" in repo_path:
        *_junk, repo_blurb = repo_path.split(":")
        org, repo_name = repo_blurb.split("/")
    else:
        org = "local"
        repo_name = Path(repo_path).name
    clone_target = cache_folder / org / repo_name
    if clone_target.is_dir():
        print("Given a URL for we cloned already: no cloning")
        return Repo(clone_target)
    print("Given a URL, cache miss: cloning")
    cloned = Repo().clone_from(
        url=repo_path,
        to_path=clone_target,
        multi_options=["--depth=1"],
    )
    return cloned


def commit(repo: Repo, driver: PatchDriver, branch_name: str):
    """Commit the repo's changes in branch_name, given the PatchDriver that did it"""
    assert repo.is_dirty(untracked_files=True), "Repo is clean, nothing to commit"
    branch = repo.create_head(branch_name)
    branch.checkout()
    repo.git.add(A=True)
    repo.git.commit(m="Bump by driver")
