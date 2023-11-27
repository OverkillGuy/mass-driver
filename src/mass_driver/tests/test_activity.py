"""Validate an 'Activity', a single file that does both Migration and Forge

Feature: Unified 'Activities' for separable migration-then-forge

"""

from pathlib import Path

import pytest

from mass_driver.forge_run import PROutcome
from mass_driver.forges.dummy import DUMMY_PR_URL
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import (
    copy_folder,
    massdrive_runlocal,
    repoize,
)


def test_migration_and_forge(tmp_path, shared_datadir, monkeypatch):
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
    repoize(repo_path)
    monkeypatch.chdir(repo_path)
    repo_id = "."
    activityconfig_filepath = shared_datadir / "activity.toml"
    # When I run mass-driver
    result = massdrive_runlocal(None, activityconfig_filepath)
    res = result.repos[repo_id]
    if res.patch is None:
        return pytest.fail("Should have a migration result")
    if res.forge is None:
        return pytest.fail("Should have a forge result")
    migration_result, forge_result = (
        res.patch,
        res.forge,
    )
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


@pytest.mark.xfail(reason="Migration-then-forge borked, known-bug")
def test_migration_then_forge(tmp_path, shared_datadir, monkeypatch):
    """Scenario: Validate migration separate from forge"""
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
    repoize(repo_path)
    monkeypatch.chdir(repo_path)
    repo_id = "."
    # Given I run mass-driver in migration
    mig_path = shared_datadir / "mig_only.toml"
    result = massdrive_runlocal(None, mig_path)
    res = result.repos[repo_id]
    # And I get OK outcome on migration
    if res.patch is None:
        return pytest.fail("Should have a migration result")
    # But no forge result initially
    if res.forge is not None:
        return pytest.fail("Should have no forge result initially")
    migration_result = res.patch
    assert (
        migration_result.outcome == PatchOutcome.PATCHED_OK
    ), "Wrong outcome from patching"
    forge_path = shared_datadir / "forge_only.toml"
    # FIXME: The forge step here asserts [r.status == PATCHED] but here only SOURCED!)
    result2 = massdrive_runlocal(None, forge_path)
    res2 = result2.repos[repo_id]
    assert res2, "Should have a second result"
    forge_result = res2.forge
    assert forge_result is not None, "Should have a forge result"
    # And PR creation is OK
    assert forge_result.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert (
        forge_result.pr_html_url == DUMMY_PR_URL
    ), "Should have returned correct PR URL"


def test_scan(tmp_path, shared_datadir):
    """Feature: Scan repositories

    As a mass-driver user
    I need to scan repo contents
    To discover what migration need to be prepared
    """
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
    activityconfig_filepath = shared_datadir / "activity.toml"
    # When I run a mass-driver scan
    repo_id = "."
    result = massdrive_runlocal(None, activityconfig_filepath)
    res = result.repos[repo_id]
    scan_result = res.scan
    # Then I get scan results
    assert scan_result is not None, "Should have a Scan result"
    assert isinstance(scan_result, dict), "Should return dict scan result"
    # And scan result is correct
    assert "root-files" in scan_result.keys(), "Should have 'root-files' Scanner"
    assert scan_result["root-files"][
        "readme_md"
    ], "Should have discovered README.md in sample repo"
