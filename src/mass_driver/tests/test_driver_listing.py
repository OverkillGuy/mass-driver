"""Validate the driver discovery

Feature: Plugin discovery
  As the mass-driver dev
  I need to ensure plugins are working
  In order to create a downstream driver plugins ecosystem

"""

import pytest

from mass_driver.discovery import get_driver
from mass_driver.patchdriver import PatchDriver


@pytest.mark.parametrize("driver_name", ["shell", "precommit", "counter"])
def test_discover_builtin_drivers(driver_name):
    """Scenario: Built-in drivers are discovered"""
    # Given a built-in PatchDriver exposed as <driver_name> plugin
    # When I look for named driver <driver_name>
    driver = get_driver(driver_name)
    # Then I get a valid PatchDriver
    assert issubclass(driver, PatchDriver), "Discovered plugin isn't a PatchDriver"
