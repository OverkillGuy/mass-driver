"""Reusable fixtures for mass-driver testing"""

import shutil
from pathlib import Path

from git import Repo

from mass_driver.cli import cli as massdriver_cli


def repoize(path: Path):
    """Create a git repo with inital commit at path"""
    repo = Repo.init(path, bare=False, initial_branch="main")
    repo.index.add("*")
    repo.index.commit("Initial commit from template")
    return path


def copy_folder(repo_data, tmp_path):
    """Copy the repo_data folder to tmp_path"""
    shutil.copytree(str(repo_data), str(tmp_path))


def massdrive(repo_url: str, activity_configfilepath: Path, repo_is_path: bool = True):
    """Run mass-driver with given driver-config over a sample LOCAL repo

    The "repo" is either a local folder path which we'll 'git init && git commit
    -Am' over, or a cloneable URL in which case we will pass it through.

    We will rely on repo_is_path variable to determine if we need to masquerade
    the local path as a git repo or not. This means if giving a proper git
    cloneable URL, set `repo_is_path=False`.

    Note:
        See pytest-datadir's "datadir" fixture for convenient data linking

    Returns:
        The PatchResult object returned by mass-driver for that repo

    """
    if repo_is_path:
        repoize(Path(repo_url))
    result = massdriver_cli(
        [
            "run",
            str(activity_configfilepath),
            "--repo-path",
            repo_url,
            "--no-pause",
        ]
    )
    mig_result = (
        result.migration_result[str(repo_url)]
        if result.migration_result is not None
        else None
    )
    for_result = (
        result.forge_result[str(repo_url)] if result.forge_result is not None else None
    )
    return mig_result, for_result
