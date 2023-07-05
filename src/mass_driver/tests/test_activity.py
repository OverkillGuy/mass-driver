"""Validate an 'Activity', a single file that does both Migration and Forge

Feature: Unified 'Activities' for separable migration-then-forge

"""

from pathlib import Path

from mass_driver.forge_run import PROutcome
from mass_driver.forges.dummy import DUMMY_PR_URL
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import (
    copy_folder,
    massdrive,
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
    migration_result, forge_result = (
        result.migration_result[repo_id],
        result.forge_result[repo_id],
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


def test_scan(tmp_path, shared_datadir, mocker):
    """Feature: Scan repositories

    As a mass-driver user
    I need to scan repo contents
    To discover what migration need to be prepared
    """
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
    activityconfig_filepath = shared_datadir / "activity.toml"
    # When I run a mass-driver scan
    _mig, _forge, scan_result = massdrive(str(repo_path), activityconfig_filepath)
    # Then I get scan results
    assert isinstance(scan_result, dict), "Should return dict scan result"
    # And scan result is correct
    assert "root-files" in scan_result.keys(), "Should have 'root-files' Scanner"
    assert scan_result["root-files"][
        "readme_md"
    ], "Should have discovered README.md in sample repo"
