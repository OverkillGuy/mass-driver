"""Test a couple of Sources"""

from mass_driver.models.repository import Repo
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
    sourced = res.repos_sourced
    assert sourced, "Should have gotten repos sourced"
    assert len(sourced) == 3, "Should have gotten 3 repos"
    repos = list(sourced.values())
    assert isinstance(repos[0], Repo), "Should have gotten a Repo back"


def test_csv_source(datadir, monkeypatch):
    """Check that the CSV source is discovered OK"""
    # Given a source config using template source
    activityconfig_filepath = datadir / "csv_source.toml"
    # And a repo template to expand
    monkeypatch.chdir(datadir)
    # When I run mass-driver
    res = massdrive_runlocal(None, activityconfig_filepath)
    # Then I get sourced repos
    sourced = res.repos_sourced
    assert sourced, "Should have gotten repos sourced"
    assert len(sourced) == 2, "Should have gotten 2 CSV repos"
    repos = list(sourced.values())
    assert isinstance(repos[0], Repo), "Should have gotten a Repo back"
    assert "extra_key" in repos[0].patch_data, "Should have parsed extra CSV field"
