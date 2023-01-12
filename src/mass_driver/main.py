"""Principal launchpoint for Mass-Driver"""

from pathlib import Path
from tempfile import mkdtemp

from mass_driver.discovery import driver_from_config
from mass_driver.forges import GithubForge
from mass_driver.migration import Migration
from mass_driver.model import Forge, PatchDriver
from mass_driver.repo import clone_if_remote, commit

DEFAULT_CACHE = Path(".mass_driver/repos/")


def main(
    config: Migration,
    repo_paths: list[str],
    dry_run: bool,
    auth_token: str,
    cache: bool,
):
    """Run the program's main command"""
    driver = driver_from_config(config)
    forge = GithubForge(auth_token)
    repo_count = len(repo_paths)
    cache_folder = DEFAULT_CACHE
    if not cache:
        cache_folder = Path(mkdtemp(suffix=".cache"))
        print(f"Using repo cache folder: {cache_folder}/ (Won't wipe it on exit!)")
    print(f"Processing {repo_count} with {driver=}")
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            process_repo(
                repo_path, driver, config, dry_run, forge, cache_path=cache_folder
            )
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            continue
    print("Action completed: exiting")


def process_repo(
    repo_path: str,
    driver: PatchDriver,
    config: Migration,
    dry_run: bool,
    forge: Forge,
    cache_path: Path,
):
    """Process a repo with Mass Driver"""
    repo = clone_if_remote(repo_path, cache_path)
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
    branch_name = config.branch_name
    if branch_name is None:  # Branchname is Optional in TOML config
        branch_name = driver.__class__.__name__.lower()
    commit(repo, driver, branch_name)
    print("Done committing")
