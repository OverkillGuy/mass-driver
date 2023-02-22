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


def massdrive(repo_path: Path, activity_configfilepath: Path):
    """Run mass-driver with given driver-config over a sample repo

    The "repo" is a folder which we'll 'git init && git commit -Am' over.

    Note:
        See pytest-datadir's "datadir" fixture for convenient data linking

    Returns:
        The PatchResult object returned by mass-driver for that repo
    """
    repoize(repo_path)
    migration_result, forge_result = massdriver_cli(
        [
            "run",
            str(activity_configfilepath),
            "--repo-path",
            str(repo_path),
            "--no-pause",
        ]
    )
    mig_result = (
        migration_result[str(repo_path)] if migration_result is not None else None
    )
    for_result = forge_result[str(repo_path)] if forge_result is not None else None
    return mig_result, for_result
