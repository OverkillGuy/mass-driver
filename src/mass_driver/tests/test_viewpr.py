"""Test the 'mass-driver view-pr' feature, relying on Forges"""

import logging

from mass_driver.cli import cli as massdriver_cli


def test_viewpr(monkeypatch, caplog):
    """Scenario: Review PRs via mass-driver"""
    caplog.set_level(logging.INFO)
    # Given a PR URL to review
    pr_url = "https://example.com/myrepo/pull/1"
    # And a configured Forge
    monkeypatch.setenv("FORGE_SOME_PARAM_FOR_FORGECONFIG", "super secret string")
    # When I review PR status via mass-driver view-pr
    result = massdriver_cli(["view-pr", "dummy", "--pr", pr_url])
    # Then the run succeeds
    assert result == 0, "Should succed running mass-driver view-pr"
    captured = caplog.records
    # The 'dummy' forge always sets PRs to 'merged' status
    error_records = [record for record in captured if record.levelname == "ERROR"]
    assert not error_records, "Shouldn't have gotten any error message"
    assert "(100.00%) merged" in caplog.text, "Should have marked the PR as merged"


def test_viewpr_dozen(monkeypatch, caplog):
    """Scenario: Review dozens of OK PRs via mass-driver"""
    caplog.set_level(logging.INFO)
    # Given a dozen PR URL to review
    pr_base_url = "https://example.com/myrepo/pull"
    pr_urls = [f"{pr_base_url}/{i}" for i in range(1, 12)]
    # And a configured Forge
    monkeypatch.setenv("FORGE_SOME_PARAM_FOR_FORGECONFIG", "super secret string")
    # When I review PR status via mass-driver view-pr
    args = []
    for pr_url in pr_urls:
        args.extend(["--pr", pr_url])
    result = massdriver_cli(["view-pr", "dummy", "--pr", *pr_urls])
    # Then the run succeeds
    assert result == 0, "Should succed running mass-driver view-pr"
    captured = caplog.records
    # The 'dummy' forge always sets PRs to 'merged' status
    error_records = [record for record in captured if record.levelname == "ERROR"]
    assert not error_records, "Shouldn't have gotten any error message"
    assert "(100.00%) merged" in caplog.text, "Should have marked the PR as merged"
