"""
Validate plugin discovery

Feature: Plugin discovery
  As the mass-driver dev
  I need to ensure plugins are working
  In order to create a downstream driver plugins ecosystem

"""

import pytest

from mass_driver.discovery import get_driver, get_forge, get_source
from mass_driver.models.forge import Forge
from mass_driver.models.patchdriver import PatchDriver
from mass_driver.models.repository import Source


@pytest.mark.parametrize("driver_name", ["shell", "precommit", "counter"])
def test_discover_builtin_drivers(driver_name):
    """Scenario: Built-in drivers are discovered"""
    # Given a built-in PatchDriver exposed as <driver_name> plugin
    # When I look for named driver <driver_name>
    driver = get_driver(driver_name)
    # Then I get a valid PatchDriver
    assert issubclass(driver, PatchDriver), "Discovered plugin isn't a PatchDriver"


@pytest.mark.parametrize("forge_name", ["dummy", "github", "github-app"])
def test_discover_builtin_forges(forge_name):
    """Scenario: Built-in forges are discovered"""
    # Given a built-in Forge exposed as <forge_name> plugin
    # When I look for named forge <forge_name>
    forge = get_forge(forge_name)
    # Then I get a valid Forge
    assert issubclass(forge, Forge), "Discovered plugin isn't a Forge"


@pytest.mark.parametrize("source_name", ["repo-list"])
def test_discover_builtin_sources(source_name):
    """Scenario: Built-in sources are discovered"""
    # Given a built-in Source exposed as <source_name> plugin
    # When I look for named source <source_name>
    source = get_source(source_name)
    # Then I get a valid Source
    assert issubclass(source, Source), "Discovered plugin isn't a Source"
