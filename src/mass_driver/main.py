"""Principal launchpoint for Mass-Driver"""

from pathlib import Path
from typing import Optional

from mass_driver.drivers import Poetry
from mass_driver.forges import GithubForge
from mass_driver.model import Forge, PatchDriver
from mass_driver.repo import clone_if_remote, commit


def main(
    repo_paths: list[str], dry_run: bool, branch_name: Optional[str], auth_token: str
):
    """Run the program's main command"""
    driver = Poetry(package="pytest", target_major="8", package_group="test")
    forge = GithubForge(auth_token)
    if not branch_name:
        branch_name = driver.__class__.__name__.lower()
    repo_count = len(repo_paths)
    print(f"Processing {repo_count} with {driver=}")
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            process_repo(repo_path, driver, dry_run, branch_name, forge)
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            continue
    print("Action completed: exiting")


def process_repo(
    repo_path: str, driver: PatchDriver, dry_run: bool, branch_name: str, forge: Forge
):
    """Process a repo with Mass Driver"""
    repo = clone_if_remote(repo_path)
    repo_as_path = Path(repo.working_dir)
    print(f"Detecting '{repo_path}' before patching...")
    needs_patch = driver.run(repo_as_path, dry_run=dry_run)
    if not needs_patch:
        print("Does not need patching: skipping")
        return
    if dry_run:
        print("Dry-run completed")
        return
    # Not a dry run: save the mutation
    print("Done patching, committing")
    commit(repo, driver, branch_name)
    print("Done committing")
