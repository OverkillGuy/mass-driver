"""Main activities of Mass-Driver: For each repo, clone it, then scan/migrate it"""

import traceback
from copy import deepcopy
from pathlib import Path

from mass_driver.git import (
    GitRepo,
    clone_if_remote,
    commit,
    get_cache_folder,
    switch_branch_then_pull,
)
from mass_driver.models.activity import (
    ActivityLoaded,
    ActivityOutcome,
    IndexedPatchResult,
    IndexedScanResult,
    ScanResult,
)
from mass_driver.models.migration import MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import (
    ClonedRepo,
    IndexedClonedRepos,
    IndexedRepos,
    Repo,
)
from mass_driver.models.scan import ScanLoaded


def run(
    activity: ActivityLoaded,
    repos: IndexedRepos,
    cache: bool,
) -> ActivityOutcome:
    """Run the main activity: over N repos, clone, then scan/patch"""
    repo_count = len(repos.keys())
    migration = activity.migration
    scan = activity.scan
    cache_folder = get_cache_folder(cache)
    cloned_repos: IndexedClonedRepos = {}
    scanner_results: IndexedScanResult | None = None
    patch_results: IndexedPatchResult | None = None
    what_array = []
    if scan is not None:
        what_array.append(f"{len(scan.scanners)} scanners")
        scanner_results = {}
    if migration is not None:
        what_array.append(f"{migration.driver=}")
        patch_results = {}
    print(f"Processing {repo_count} with {' and '.join(what_array)}")
    for repo_index, (repo_id, repo) in enumerate(repos.items(), start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_id}...")
            cloned_repo, repo_gitobj = clone_repo(repo, cache_folder)
            cloned_repos[repo_id] = cloned_repo
        except Exception as e:
            print(f"Error cloning repo '{repo_id}'\nError was: {e}")
            continue
        if scan and scanner_results is not None:
            try:
                scan_result = scan_repo(scan, cloned_repo)
                scanner_results[repo_id] = scan_result
            except Exception as e:
                print(f"Error scanning repo '{repo_id}'\nError was: {e}")
                # Reaching here should be impossible (catch-all in scan)
        if migration and patch_results is not None:
            try:
                # Ensure no driver persistence between repos
                migration_copy = deepcopy(migration)
                result, excep = migrate_repo(cloned_repo, repo_gitobj, migration_copy)
                patch_results[repo_id] = result
            except Exception as e:
                print(f"Error migrating repo '{repo_id}'\nError was: {e}")
                patch_results[repo_id] = PatchResult(
                    outcome=PatchOutcome.PATCH_ERROR,
                    details=f"Unhandled exception caught during patching. Error was: {e}",
                )
    print("Action completed: exiting")
    return ActivityOutcome(
        repos_sourced=repos,
        repos_cloned=cloned_repos,
        scan_result=scanner_results,
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


def migrate_repo(
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


def scan_repo(
    config: ScanLoaded,
    cloned_repo: ClonedRepo,
) -> ScanResult:
    """Apply all Scanners on a single repo"""
    scan_result: ScanResult = {}
    for scanner in config.scanners:
        try:
            scan_result[scanner.name] = scanner.func(cloned_repo.cloned_path)
        except Exception as e:
            scan_result[scanner.name] = {
                "scan_error": {
                    "exception": str(e),
                    "backtrace": traceback.format_exception(e),
                }
            }
    return scan_result
