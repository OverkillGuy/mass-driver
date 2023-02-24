"""Principal launchpoint for Mass-Driver"""

from copy import deepcopy
from pathlib import Path
from tempfile import mkdtemp

from mass_driver.models.activity import (
    ActivityOutcome,
    IndexedPatchResult,
    RepoPathLookup,
    RepoUrl,
)
from mass_driver.models.migration import MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.repo import clone_if_remote, commit

DEFAULT_CACHE = Path(".mass_driver/repos/")


def main(
    migration: MigrationLoaded,
    repo_urls: list[RepoUrl],
    cache: bool,
) -> ActivityOutcome:
    """Run the program's main command"""
    repo_count = len(repo_urls)
    cache_folder = DEFAULT_CACHE
    if not cache:
        cache_folder = Path(mkdtemp(suffix=".cache"))
        print(f"Using repo cache folder: {cache_folder}/ (Won't wipe it on exit!)")
    print(f"Processing {repo_count} with {migration.driver=}")
    patch_results: IndexedPatchResult = {}
    repo_local_paths: RepoPathLookup = {}
    for repo_index, repo_url in enumerate(repo_urls, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_url}...")
            # Ensure no driver persistence between repos
            migration_copy = deepcopy(migration)
            result, repo_local_path, excep = process_repo(
                repo_url, migration_copy, cache_path=cache_folder
            )
            patch_results[repo_url] = result
            repo_local_paths[repo_url] = repo_local_path
            # if excep is not None:
        except Exception as e:
            print(f"Error processing repo '{repo_url}'\nError was: {e}")
            patch_results[repo_url] = result = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            repo_local_paths[repo_url] = repo_local_path  # Cannot trust the repo
            continue
    print("Action completed: exiting")
    return ActivityOutcome(
        repos_input=repo_urls,
        local_repos_path=repo_local_paths,
        migration_result=patch_results,
    )


def process_repo(
    repo_url: str,
    migration: MigrationLoaded,
    cache_path: Path,
) -> tuple[PatchResult, Path, Exception | None]:
    """Process a repo with Mass Driver"""
    repo_gitobj = clone_if_remote(repo_url, cache_path)
    repo_local_path = Path(repo_gitobj.working_dir)
    try:
        result = migration.driver.run(repo_local_path)
    except Exception as e:
        result = PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details=f"Unhandled exception caught during patching. Error was: {e}",
        )
        return (result, repo_local_path, e)
    print(result.outcome.value)
    if result.outcome != PatchOutcome.PATCHED_OK:
        return (result, repo_local_path, None)
    # Patched OK: Save the mutation
    commit(repo_gitobj, migration)
    return (result, repo_local_path, None)
