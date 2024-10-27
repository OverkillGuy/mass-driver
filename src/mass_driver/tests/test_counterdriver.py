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

# test-start marker
from pathlib import Path

import pytest

from mass_driver.tests.fixtures import copy_folder, massdrive_check_file

# Go from this filename.py to folder:
# ./test_counterdriver.py -> ./test_counterdriver/
TESTS_FOLDER = Path(__file__).with_suffix("")


@pytest.mark.parametrize(
    "test_folder", [f.name for f in TESTS_FOLDER.iterdir() if f.is_dir()]
)
def test_driver_one(test_folder: Path, tmp_path):
    """Check a single pattern"""
    absolute_reference = TESTS_FOLDER / test_folder
    workdir = tmp_path / "repo"
    copy_folder(absolute_reference, workdir)
    result, reference = massdrive_check_file(workdir)
    assert result == reference, "Massdriver result should match reference"
    # test-end marker
