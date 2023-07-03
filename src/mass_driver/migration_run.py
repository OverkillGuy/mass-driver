"""Principal launchpoint for Mass-Driver"""

from copy import deepcopy
from pathlib import Path

from mass_driver.models.activity import ActivityOutcome, IndexedPatchResult
from mass_driver.models.migration import MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import (
    ClonedRepo,
    IndexedClonedRepos,
    IndexedRepos,
    Repo,
)
from mass_driver.repo import (
    GitRepo,
    clone_if_remote,
    commit,
    get_cache_folder,
    switch_branch_then_pull,
)


def main(
    migration: MigrationLoaded,
    repos: IndexedRepos,
    cache: bool,
) -> ActivityOutcome:
    """Run the program's main command"""
    repo_count = len(repos.keys())
    cache_folder = get_cache_folder(cache)
    cloned_repos: IndexedClonedRepos = {}
    print(f"Processing {repo_count} with {migration.driver=}")
    patch_results: IndexedPatchResult = {}
    for repo_index, (repo_id, repo) in enumerate(repos.items(), start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_id}...")
            # Ensure no driver persistence between repos
            migration_copy = deepcopy(migration)
            cloned_repo, repo_gitobj = clone_repo(repo, cache_folder)
            cloned_repos[repo_id] = cloned_repo
            result, excep = process_repo(cloned_repo, repo_gitobj, migration_copy)
            patch_results[repo_id] = result
            # if excep is not None:
        except Exception as e:
            print(f"Error processing repo '{repo_id}'\nError was: {e}")
            patch_results[repo_id] = result = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            cloned_repos[repo_id] = cloned_repo  # TODO Can I trust this path?
            continue
    print("Action completed: exiting")
    return ActivityOutcome(
        repos_sourced=repos,
        repos_cloned=cloned_repos,
        migration_result=patch_results,
    )


def clone_repo(repo: Repo, cache_path: Path) -> tuple[ClonedRepo, GitRepo]:
    """Clone a repo (if needed) and switch branch"""
    repo_gitobj = clone_if_remote(repo.clone_url, cache_path)
    switch_branch_then_pull(repo_gitobj, repo.force_pull, repo.upstream_branch)
    repo_local_path = Path(repo_gitobj.working_dir)
    cloned_repo = ClonedRepo(
        cloned_path=repo_local_path,
        current_branch=repo_gitobj.active_branch.name,
        **repo.dict(),
    )
    return cloned_repo, repo_gitobj


def process_repo(
    cloned_repo: ClonedRepo,
    repo_gitobj: GitRepo,
    migration: MigrationLoaded,
) -> tuple[PatchResult, Exception | None]:
    """Process a repo with Mass Driver"""
    # FIXME: IndexedRepos is map of Repo not ClonedRepos, causing chaos
    # Solution is to move cloning to pre-migration(?) and keep ClonedRepo maps everywhere?
    try:
        result = migration.driver.run(cloned_repo)
    except Exception as e:
        result = PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details=f"Unhandled exception caught during patching. Error was: {e}",
        )
        return (result, e)
    print(result.outcome.value)
    if result.outcome != PatchOutcome.PATCHED_OK:
        return (result, None)
    # Patched OK: Save the mutation
    commit(repo_gitobj, migration)
    return (result, None)
