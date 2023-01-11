"""Reusable fixtures for mass-driver testing"""

import shutil
from collections import namedtuple
from pathlib import Path

from git import Repo

from mass_driver.cli import cli as massdriver_cli
from mass_driver.discovery import driver_from_config

MassdriveTest = namedtuple("MassdriveTest", ["repo_path", "driver", "config_file"])
"""Alias for tuple of returned info, after mass-driver ran"""


def repoize(path: Path):
    """Create a git repo with inital commit at path"""
    repo = Repo.init(path, bare=False)
    repo.index.add(".")
    repo.index.commit("Initial commit from template")
    return path


def copy_folder(repo_data, tmp_path):
    """Copy the repo_data folder to tmp_path"""
    shutil.copytree(str(repo_data), str(tmp_path))


def massdrive(repo_path: Path, driver_configfilepath: Path) -> MassdriveTest:
    """Run mass-driver with given driver-config over a sample repo

    The "repo" is a folder which we'll 'git init && git commit -Am' over.


    Args:
        repo_path:

    Note:
        See pytest-datadir's "datadir" fixture for convenient data linking
    """
    repoize(repo_path)
    massdriver_cli(
        [
            "run",
            str(driver_configfilepath),
            "--really-commit-changes",
            "--repo-path",
            str(repo_path),
        ]
    )
    driver = driver_from_config(driver_configfilepath.read_text())
    return MassdriveTest(repo_path, driver, driver_configfilepath)
