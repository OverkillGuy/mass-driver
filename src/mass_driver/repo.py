"""Cloning remote repos (repos not using local path)"""

from pathlib import Path

from git import Repo

from mass_driver.migration import Migration


def clone_if_remote(repo_path: str, cache_folder: Path) -> Repo:
    """Build a git Repo; If repo_path isn't a directory, clone it"""
    if Path(repo_path).is_dir():
        print("Given an existing (local) repo: no cloning")
        return Repo(path=repo_path)
    # SSH clone URL e.g: git@github.com:OverkillGuy/python-template
    if ":" in repo_path:  # Presence of : is proxy for SSH clone URL
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
    cloned = Repo.clone_from(
        url=repo_path,
        to_path=clone_target,
        multi_options=["--depth=1"],
    )
    return cloned


def commit(repo: Repo, migration: Migration):
    """Commit the repo's changes in branch_name, given the PatchDriver that did it"""
    assert repo.is_dirty(untracked_files=True), "Repo shouldn't be clean on committing"
    branch = repo.create_head(migration.branch_name)
    branch.checkout()
    repo.git.add(A=True)
    repo.git.commit(m=migration.commit_message)


def push(repo: Repo, branch_name: str):
    """Push a branch of the repo to a remote"""
    remote = repo.remote()
    remote.push(refspec=branch_name)
