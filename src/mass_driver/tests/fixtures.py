"""Reusable fixtures for mass-driver testing"""

import shutil
from pathlib import Path

from git import Repo

from mass_driver.cli import cli as massdriver_cli
from mass_driver.models.patchdriver import PatchOutcome


def repoize(path: Path):
    """Create a git repo with inital commit at path"""
    repo = Repo.init(path, bare=False)
    repo.index.add("*")
    repo.index.commit("Initial commit from template")
    return path


def copy_folder(repo_data, tmp_path):
    """Copy the repo_data folder to tmp_path"""
    shutil.copytree(str(repo_data), str(tmp_path))


def massdrive(repo_path: Path, migration_configfilepath: Path):
    """Run mass-driver with given driver-config over a sample repo

    The "repo" is a folder which we'll 'git init && git commit -Am' over.

    Note:
        See pytest-datadir's "datadir" fixture for convenient data linking

    Returns:
        The PatchResult object returned by mass-driver for that repo
    """
    repoize(repo_path)
    result_dict = massdriver_cli(
        [
            "run-migration",
            str(migration_configfilepath),
            "--really-commit-changes",
            "--repo-path",
            str(repo_path),
        ]
    )
    return result_dict[str(repo_path)]


def massdrive_and_forge(
    repo_path: Path, migration_configfilepath: Path, forge_configfilepath: Path
):
    """Apply a forge after mass-driver run-migration"""
    massdrive_result = massdrive(repo_path, migration_configfilepath)
    assert (
        massdrive_result.outcome == PatchOutcome.PATCHED_OK
    ), "Should Patch OK before running Forge test"
    result_dict = massdriver_cli(
        [
            "run-forge",
            str(forge_configfilepath),
            "--repo-path",
            str(repo_path),
        ]
    )
    return result_dict[str(repo_path)]
