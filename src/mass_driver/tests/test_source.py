"""Test a couple of Sources"""

from mass_driver.tests.fixtures import massdrive_runlocal


def test_template_source(datadir, monkeypatch):
    """Check that the source is discovered OK"""
    # Given a source config using template source
    activityconfig_filepath = datadir / "template_source.toml"
    # And a repo template to expand
    monkeypatch.chdir(datadir)
    # When I run mass-driver
    res = massdrive_runlocal(None, activityconfig_filepath)
    # Then I get sourced repos
    repos = res.repos
    assert repos, "Should have gotten repos sourced"
    assert len(repos) == 3, "Should have gotten 3 repos"


def test_csv_source(datadir, monkeypatch):
    """Check that the CSV source is discovered OK"""
    # Given a source config using template source
    activityconfig_filepath = datadir / "csv_source.toml"
    # And a repo template to expand
    monkeypatch.chdir(datadir)
    # When I run mass-driver
    res = massdrive_runlocal(None, activityconfig_filepath)
    # Then I get sourced repos
    repos = res.repos
    assert repos, "Should have gotten repos sourced"
    assert len(repos) == 2, "Should have gotten 2 CSV repos"
    first_repo = next(iter(repos.values()))  # First item of the iterable of dict
    assert first_repo.source is not None, "First repo soruced should have source field"
    assert (
        "extra_key" in first_repo.source.patch_data
    ), "Should have parsed extra CSV field"
