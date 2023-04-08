"""Demonstrate the Scanner test fixture

Feature: Scanner test fixtures
  As a mass-driver plugin dev
  I need to test my future scanner on sample repos
  In order to ship scanner plugins efficiently
"""

from pathlib import Path

import pytest

from mass_driver.tests.fixtures import copy_folder, massdrive_scan_check

# Go from this filename.py to folder:
# ./test_scanner.py -> ./test_scanner/
TESTS_FOLDER = Path(__file__).with_suffix("")


@pytest.mark.parametrize(
    "test_folder", [f.name for f in TESTS_FOLDER.iterdir() if f.is_dir()]
)
def test_scanner(test_folder: Path, tmp_path):
    """Scenario: Check the sample folder scan results"""
    absolute_reference = TESTS_FOLDER / test_folder
    workdir = tmp_path / "repo"
    copy_folder(absolute_reference, workdir)
    result, ref = massdrive_scan_check(workdir)
    assert result == ref, "Scan results should match reference"
