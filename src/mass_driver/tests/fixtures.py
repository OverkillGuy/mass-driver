"""Reusable fixtures for mass-driver testing"""

import json
import shutil
import sys
from pathlib import Path

from git import Repo

from mass_driver.cli import cli as massdriver_cli
from mass_driver.models.patchdriver import PatchOutcome


def repoize(path: Path):
    """Create a git repo with inital commit at path"""
    repo = Repo.init(path, bare=False, initial_branch="main")
    repo.index.add("*")
    repo.index.commit("Initial commit from template")
    return path


def copy_folder(repo_data, tmp_path):
    """Copy the repo_data folder to tmp_path"""
    shutil.copytree(str(repo_data), str(tmp_path))


def massdrive(repo_url: str, activity_configfilepath: Path, repo_is_path: bool = True):
    """Run mass-driver with given driver-config over a sample LOCAL repo

    The "repo" is either a local folder path which we'll 'git init && git commit
    -Am' over, or a cloneable URL in which case we will pass it through.

    We will rely on repo_is_path variable to determine if we need to masquerade
    the local path as a git repo or not. This means if giving a proper git
    cloneable URL, set `repo_is_path=False`.

    Note:
        See pytest-datadir's "datadir" fixture for convenient data linking

    Returns:
        The PatchResult object returned by mass-driver for that repo

    """
    if repo_is_path:
        repoize(Path(repo_url))
    result = massdriver_cli(
        [
            "run",
            str(activity_configfilepath),
            "--repo-path",
            repo_url,
            "--no-pause",
        ]
    )
    mig_result = (
        result.migration_result[str(repo_url)]
        if result.migration_result is not None
        else None
    )
    for_result = (
        result.forge_result[str(repo_url)] if result.forge_result is not None else None
    )
    return mig_result, for_result


def massdrive_check_file(workdir: Path):
    """Run mass-driver migration.toml over input.yaml and check the output.yaml matches"""
    config_file = workdir / "migration.toml"
    input_file = workdir / "input.txt"
    reference_file = workdir / "output.txt"
    outcome_file = workdir / "outcome.txt"
    details_file = workdir / "details.txt"
    try:
        migration_result, _forge_result = massdrive(
            str(workdir),
            config_file,
        )
    except Exception as e:
        print("Error during mass-driver run", file=sys.stderr)
        raise e
    if outcome_file.exists():
        assert migration_result.outcome == PatchOutcome(
            outcome_file.read_text().strip()
        ), "Should patch"
        if details_file.exists():
            assert (
                details_file.read_text().casefold()
                in migration_result.details.casefold()
            ), "Details should match up"
        return None, None  # Return empties for assert equals checks
    else:
        assert migration_result.outcome == PatchOutcome.PATCHED_OK, "Should patch OK"
        mutated = input_file.read_text()
        reference = reference_file.read_text()
        return mutated, reference


def massdrive_scan(
    repo_url: str, activity_configfilepath: Path, repo_is_path: bool = True
):
    """Run mass-driver scan over a given local repo"""
    if repo_is_path:
        repoize(Path(repo_url))
    result = massdriver_cli(
        [
            "scan",
            str(activity_configfilepath),
            "--repo-path",
            repo_url,
        ]
    )
    return result.scan_result[str(repo_url)] if result.scan_result is not None else None


def massdrive_scan_check(workdir: Path):
    """Scan mass-driver over workdir and check the scan_results.json matches"""
    reference_results_file = workdir / "scan_results.json"
    config_file = workdir / "activity.toml"
    try:
        scan_results = massdrive_scan(
            str(workdir),
            config_file,
        )
    except Exception as e:
        print("Error during mass-driver scan", file=sys.stderr)
        raise e
    reference_results = json.loads(reference_results_file.read_text())
    return scan_results, reference_results
