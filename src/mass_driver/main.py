"""Principal launchpoint for Mass-Driver"""

from pathlib import Path
from typing import Optional

from mass_driver.drivers import Counter
from mass_driver.forges import GithubForge
from mass_driver.model import Forge, PatchDriver
from mass_driver.repo import clone_if_remote, commit


def main(
    repo_paths: list[str], do_patch: bool, branch_name: Optional[str], auth_token: str
):
    """Run the program's main command"""
    driver = Counter(counter_file=Path("counter"), target_count=1)
    forge = GithubForge(auth_token)
    if not branch_name:
        branch_name = driver.__class__.__name__.lower()
    repo_count = len(repo_paths)
    print(f"Processing {repo_count} with {driver=}")
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            process_repo(repo_path, driver, do_patch, branch_name, forge)
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            continue
    print("Action completed: exiting")


def process_repo(
    repo_path: str, driver: PatchDriver, do_patch: bool, branch_name: str, forge: Forge
):
    """Process a repo with Mass Driver: detect or patch"""
    repo = clone_if_remote(repo_path)
    if do_patch:
        print(f"Detecting '{repo_path}' before patching...")
        needs_patch = driver.detect(repo.working_dir)
        if not needs_patch:
            print("Does not need patching: skipping")
            return
        driver.patch(repo.working_dir)
        print("Done patching, committing")
        commit(repo, driver, branch_name)
        print("Done committing")
    else:
        needs_patch = driver.detect(repo.working_dir)
        print(f"Detecting '{repo_path}': {needs_patch=}")
