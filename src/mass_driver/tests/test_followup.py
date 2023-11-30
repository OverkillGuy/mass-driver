"""Check the retention: 2 migrations, 1 successful, creates 1 PR"""
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


def test_2migration_but_1forge(tmp_path, shared_datadir, monkeypatch):
    """Scenario: Forge a single time when 2 migration but only one fails"""
    # Given two repos to migrate
    repo1_path = Path(tmp_path / "test_repo1/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo1_path)
    repoize(repo1_path)
    repo1_id = "./test_repo1"

    repo2_path = Path(tmp_path / "test_repo2/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo2_path)
    (repo2_path / "counter.txt").write_text("2")  # This one's ALREADY_PATCHED!
    repoize(repo2_path)
    monkeypatch.chdir(tmp_path)
    repo2_id = "./test_repo2"

    activityconfig_filepath = shared_datadir / "2mig_1forge.toml"
    # When I run mass-driver with 2 migrations, 1 forge
    results = massdrive_runlocal(None, activityconfig_filepath)
    assert results is not None, "Should have a result"
    result1 = results.repos[repo1_id]
    assert result1.patch is not None, "Should have a migration result"
    result2 = results.repos[repo2_id]
    mig1 = result1.patch
    # Then I get OK outcome on migration1
    assert mig1.outcome == PatchOutcome.PATCHED_OK, "Wrong outcome from patching"
    # And I get ALREADY_PATCHED outcome on migration2
    mig2 = result2.patch
    assert mig2 is not None, "Should have a migration result"
    assert mig2.outcome == PatchOutcome.ALREADY_PATCHED, "Wrong outcome from patching"

    assert result1.forge is not None, "Should have a forge result"
    # And I get only 1 forge result
    forge1 = result1.forge
    assert forge1 is not None, "Should have a forge result for mig1"
    assert forge1.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert forge1.pr_html_url == DUMMY_PR_URL, "Should have returned correct PR URL"


@pytest.mark.xfail(reason="Clone1 failure, bad test for now? known bug too")
def test_1badclone_but_1forge(tmp_path, shared_datadir, monkeypatch):
    """Scenario: Forge a single time given 2 migration but 1 failed cloning"""
    # Given two repos to migrate
    repo1_path = Path(tmp_path / "test_repo1/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo1_path)
    repoize(repo1_path)
    repo1_id = "./test_repo1"

    # But the second one doesn't exist on disk
    repo2_id = "./test_repo2"

    activityconfig_filepath = shared_datadir / "2mig_1forge.toml"
    # When I run mass-driver with 2 migrations to forge
    results = massdrive_runlocal(None, activityconfig_filepath)
    assert results is not None, "Should have a result"
    result1 = results.repos[repo1_id]
    assert result1.error is None, "Should have no error for mig1"
    assert result1.patch is not None, "Should have a migration result"
    result2 = results.repos[repo2_id]
    mig1 = result1.patch
    # Then I get OK outcome on migration1
    assert mig1.outcome == PatchOutcome.PATCHED_OK, "Wrong outcome from patching"
    # And I get ALREADY_PATCHED outcome on migration2
    mig2 = result2.patch
    assert mig2 is not None, "Should have a migration result"
    assert mig2.outcome == PatchOutcome.PATCH_ERROR, "Wrong outcome from patching"

    assert result1.forge is not None, "Should have a forge result"
    # And I get only 1 forge result
    forge1 = result1.forge
    assert forge1 is not None, "Should have a forge result for mig1"
    assert forge1.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert forge1.pr_html_url == DUMMY_PR_URL, "Should have returned correct PR URL"
