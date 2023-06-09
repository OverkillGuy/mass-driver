"""Principal launchpoint for Mass-Driver"""

from copy import deepcopy
from pathlib import Path

from mass_driver.models.activity import ActivityOutcome, IndexedPatchResult
from mass_driver.models.migration import MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import IndexedRepos, Repo
from mass_driver.repo import clone_if_remote, commit, get_cache_folder


def main(
    migration: MigrationLoaded,
    repos: IndexedRepos,
    cache: bool,
) -> ActivityOutcome:
    """Run the program's main command"""
    repo_count = len(repos.keys())
    cache_folder = get_cache_folder(cache)
    cloned_repos = deepcopy(repos)
    print(f"Processing {repo_count} with {migration.driver=}")
    patch_results: IndexedPatchResult = {}
    for repo_index, (repo_id, repo) in enumerate(repos.items(), start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_id}...")
            # Ensure no driver persistence between repos
            migration_copy = deepcopy(migration)
            result, repo_local_path, excep = process_repo(
                repo, migration_copy, cache_path=cache_folder
            )
            patch_results[repo_id] = result
            cloned_repos[repo_id].cloned_path = repo_local_path
            # if excep is not None:
        except Exception as e:
            print(f"Error processing repo '{repo_id}'\nError was: {e}")
            patch_results[repo_id] = result = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            repos[repo_id].cloned_path = repo_local_path  # TODO Can I trust this path?
            continue
    print("Action completed: exiting")
    return ActivityOutcome(
        repos_sourced=cloned_repos,
        migration_result=patch_results,
    )


def process_repo(
    repo: Repo,
    migration: MigrationLoaded,
    cache_path: Path,
) -> tuple[PatchResult, Path, Exception | None]:
    """Process a repo with Mass Driver"""
    repo_gitobj = clone_if_remote(repo.clone_url, cache_path)
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
