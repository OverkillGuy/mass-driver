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
    result = massdrive_runlocal(None, activityconfig_filepath)
    if result is None:
        # Note: "return" is to trick mypy to the early-exit of pytest.fail()
        return pytest.fail("Should have a result")
    if result.migration_result is None:
        return pytest.fail("Should have a migration result")
    mig1 = result.migration_result[repo1_id]
    mig2 = result.migration_result[repo2_id]
    # Then I get OK outcome on migration1
    assert mig1.outcome == PatchOutcome.PATCHED_OK, "Wrong outcome from patching"
    # And I get ALREADY_PATCHED outcome on migration2
    assert mig2.outcome == PatchOutcome.ALREADY_PATCHED, "Wrong outcome from patching"

    if result.forge_result is None:
        return pytest.fail("Should have a forge result")
    # And I get only 1 forge result
    assert len(result.forge_result.keys()) == 1, "Should get only one forge result"
    forge1 = result.forge_result[repo1_id]
    if forge1 is None:
        return pytest.fail("Should have a forge result for mig1")

    assert forge1.outcome == PROutcome.PR_CREATED, "Should succeed creating PR"
    # And I get the PR URL I want
    assert forge1.pr_html_url == DUMMY_PR_URL, "Should have returned correct PR URL"
