"""Principal launchpoint for Mass-Driver"""

from pathlib import Path
from tempfile import mkdtemp

from mass_driver.migration import Migration, MigrationFile, load_driver
from mass_driver.patchdriver import PatchOutcome, PatchResult
from mass_driver.repo import clone_if_remote, commit

DEFAULT_CACHE = Path(".mass_driver/repos/")


def main(
    config: MigrationFile,
    repo_paths: list[str],
    dry_run: bool,
    auth_token: str,
    cache: bool,
):
    """Run the program's main command"""
    migration = load_driver(config)
    # forge = GithubForge(auth_token)
    repo_count = len(repo_paths)
    cache_folder = DEFAULT_CACHE
    if not cache:
        cache_folder = Path(mkdtemp(suffix=".cache"))
        print(f"Using repo cache folder: {cache_folder}/ (Won't wipe it on exit!)")
    print(f"Processing {repo_count} with {migration.driver=}")
    patch_results = {}
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            result = process_repo(
                repo_path, migration, dry_run, cache_path=cache_folder
            )
            patch_results[repo_path] = result
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            patch_results[repo_path] = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            continue
    print("Action completed: exiting")
    return patch_results


def process_repo(
    repo_path: str,
    migration: Migration,
    dry_run: bool,
    # forge: Forge,
    cache_path: Path,
) -> PatchResult:
    """Process a repo with Mass Driver"""
    repo = clone_if_remote(repo_path, cache_path)
    repo_as_path = Path(repo.working_dir)
    result = migration.driver.run(repo_as_path)
    print(result.outcome.value)
    if dry_run:
        print("Dry-run completed")
        return result
    if result.outcome != PatchOutcome.PATCHED_OK:
        print("Patch wasn't OK: skip commit")
        return result
    # Not a dry run: save the mutation
    print("Done patching, committing")
    commit(repo, migration)
    print("Done committing")
    return result
