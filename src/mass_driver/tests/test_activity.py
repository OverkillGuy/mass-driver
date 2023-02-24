"""Validate an 'Activity', a single file that does both Migration and Forge

Feature: Unified 'Activities' for separable migration-then-forge

"""

import os
from pathlib import Path

from mass_driver.forge_run import PROutcome
from mass_driver.forges.dummy import DUMMY_PR_URL
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive


def test_migration_and_forge(tmp_path, shared_datadir, mocker):
    """Feature: Validate the Forge CLI

         As the mass-driver dev
         I need to ensure run command works (migration then forge)
         To avoid regressions of the overall CLI

    Note that this is NOT a test of the specific Forge, as we intentionally
    stripped this forge of any real complexity, this is instead a check that the CLI
    pipeline still works.
    """
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
    activityconfig_filepath = shared_datadir / "activity.toml"
    # And a pretend token
    mocker.patch.dict(os.environ, {"FORGE_TOKEN": "ghp_supersecrettoken"})
    # When I run mass-driver
    migration_result, forge_result = massdrive(str(repo_path), activityconfig_filepath)
    # Then I get OK outcome on migration
    assert (
        migration_result.outcome == PatchOutcome.PATCHED_OK
    ), "Wrong outcome from patching"
    # And PR creation is OK
    assert forge_result.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert (
        forge_result.pr_html_url == DUMMY_PR_URL
    ), "Should have returned correct PR URL"


def test_migration_and_forge_interneturl(tmp_path, shared_datadir, mocker):
    """Scenario: Check a Migration + Forge activity still works with github clone URL

    Targets an early bug where the Forge step _required_ a local Path, which the
    Migrations would NOT provide when given an internet URL, causing potential
    crashes.

    """
    # Guaranteed to have a counter file for PATCHED_OK
    repo_url = "git@github.com:OverkillGuy/sphinx-needs-test.git"
    activityconfig_filepath = shared_datadir / "activity.toml"
    # And a pretend token
    mocker.patch.dict(os.environ, {"FORGE_TOKEN": "ghp_supersecrettoken"})
    # When I run mass-driver
    prev_cwd = os.getcwd()
    os.chdir(tmp_path)  # Ensure .mass_driver/ cache folder is disposable
    # Only applicable to the internet clone test since only it creates new folder
    migration_result, forge_result = massdrive(
        repo_url, activityconfig_filepath, repo_is_path=False
    )
    os.chdir(prev_cwd)
    # Then I get OK outcome on migration
    assert (
        migration_result.outcome == PatchOutcome.PATCHED_OK
    ), "Wrong outcome from patching"
    # And PR creation is OK
    assert forge_result.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert (
        forge_result.pr_html_url == DUMMY_PR_URL
    ), "Should have returned correct PR URL"
