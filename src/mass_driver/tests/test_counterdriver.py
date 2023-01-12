"""Tests to validate the Counter driver is valid

Counter is just about the simplest driver we can make, so showcasing it is kinda neat.#


Feature: Validate the Counter Driver
  As the mass-driver dev
  I need to write test harness for a simple PatchDriver
  To template it for downstream plugin-driver developers

Sample config files counter_config1.toml and counter_config2.toml are set up for the
Counter driver with target values 1 and 2 respectively, with counter's in-repo data
being set to 1. This validates both the case for bumping by 1, and the case where
bumping is not needed.

"""

from pathlib import Path

import pytest

from mass_driver.discovery import driver_from_config
from mass_driver.migration import load_migration
from mass_driver.tests.fixtures import copy_folder, massdrive


@pytest.mark.parametrize(
    "configfilename", ["counter_config1.toml", "counter_config2.toml"]
)
def test_counter_bumped(tmp_path, datadir, configfilename):
    """Scenario: Counter file bumped properly"""
    # Given a sample repo to mass-drive
    # And sample repo has counter at value 1
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    config_filepath = datadir / configfilename
    migration = load_migration(config_filepath.read_text())
    driver = driver_from_config(migration)
    # When I run mass-driver
    massdrive(
        repo_path,
        config_filepath,
    )
    counter_text_post = (repo_path / driver.counter_file).read_text()
    # Then the counter is bumped to config value
    assert int(counter_text_post) == driver.target_count, "Counter not updated properly"


def test_counter_borked(
    tmp_path,
    datadir,
):
    """Scenario: Counter not an integer crashes"""
    # Given a sample repo to mass-drive
    # But counter is not digits
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(datadir / "sample_repo"), repo_path)
    config_fullpath = datadir / "counter_config2.toml"
    migration = load_migration(config_fullpath.read_text())
    driver = driver_from_config(migration)
    with open(repo_path / driver.counter_file, "w") as counter_fd:
        counter_fd.write("Hello World! Not an integer!")
    # When I run mass-driver
    massdrive(repo_path, config_fullpath)
    # TODO Then some error handling should occur
