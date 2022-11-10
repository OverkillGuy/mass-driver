"""Basic tests of mass_driver CLI"""

from mass_driver.cli import cli

API_AUTH_TOK = "not-a-real-pass123deadb0b"


def test_cli_shows_usage(capsys):
    """Checks we can invoke the CLI entrypoint (no shelling out) via --help"""
    try:
        cli([])
    except SystemExit:  # Args parsing failure throws SystemExit
        pass  # Ignore it to run tests properly
    _out, err = capsys.readouterr()
    assert "usage" in err, "Missing required args should show usage in stderr"
