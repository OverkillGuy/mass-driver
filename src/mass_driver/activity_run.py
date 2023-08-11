"""Main activities of Mass-Driver: For each repo, clone it, then scan/migrate it"""

import logging
import traceback
from concurrent import futures
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
    logger = logging.getLogger("run")
    repo_count = len(repos.keys())
    migration = activity.migration
    scan = activity.scan
    cache_folder = get_cache_folder(cache, logger=logger)
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

    logger.info(f"Processing {repo_count} with {' and '.join(what_array)}")

    futures_map = {}
    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        for repo_id, repo in repos.items():
            repo_logger_name = f"repo.{repo_id}"
            repo_logger = logging.getLogger(repo_logger_name)

            future_obj = executor.submit(
                per_repo_process,
                repo_id,
                repo,
                activity,
                repo_logger,
                cache_folder,
                repo_count,
            )
            futures_map[future_obj] = repo_id
        # Submitted the jobs: iterate on completion
        for repo_index, future in enumerate(futures.as_completed(futures_map), start=1):
            repo_id = futures_map[future]
            cloned_repo, scan_result, patch_result = future.result()
            logger.info(f"[{repo_index:04d}/{repo_count:04d}] Processed {repo_id}")
            cloned_repos[repo_id] = cloned_repo
            if scanner_results is not None:
                scanner_results[repo_id] = scan_result
            if patch_results is not None:
                patch_results[repo_id] = patch_result
    logger.info("Action completed: exiting")
    return ActivityOutcome(
        repos_sourced=repos,
        repos_cloned=cloned_repos,
        scan_result=scanner_results,
        migration_result=patch_results,
    )


def per_repo_process(repo_id, repo, activity, logger, cache_folder, repo_count):
    """Process a single repo, in-thread"""
    try:
        logger.info(f"Processing {repo_id}...")
        cloned_repo, repo_gitobj = clone_repo(repo, cache_folder, logger=logger)
    except Exception as e:
        logger.info(f"Error cloning repo '{repo_id}'\nError was: {e}")
        raise e  # FIXME: Use custom exeption for capturing error here
    scan_result: ScanResult | None = None
    if activity.scan is not None:
        try:
            scan_result = scan_repo(activity.scan, cloned_repo)
        except Exception as e:
            logger.error(f"Error scanning repo '{repo_id}'")
            logger.error(f"Error was: {e}")
            # Reaching here should be impossible (catch-all in scan)
    patch_result: PatchResult | None = None
    if activity.migration:
        try:
            # Ensure no driver persistence between repos
            migration_copy = deepcopy(activity.migration)
            patch_result, excep = migrate_repo(
                cloned_repo, repo_gitobj, migration_copy, logger=logger
            )
        except Exception as e:
            logger.error(f"Error migrating repo '{repo_id}'")
            logger.error(f"Error was: {e}")
            patch_result = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )  # FIXME: Catch custom-exception into the PatchResult object
    return (cloned_repo, scan_result, patch_result)


def clone_repo(
    repo: Repo, cache_path: Path, logger: logging.Logger
) -> tuple[ClonedRepo, GitRepo]:
    """Clone a repo (if needed) and switch branch"""
    repo_gitobj = clone_if_remote(repo.clone_url, cache_path, logger=logger)
    switch_branch_then_pull(repo_gitobj, repo.force_pull, repo.upstream_branch)
    repo_local_path = Path(repo_gitobj.working_dir)
    cloned_repo = ClonedRepo(
        cloned_path=repo_local_path,
        current_branch=repo_gitobj.active_branch.name,
        **repo.dict(),
    )
    return cloned_repo, repo_gitobj


# FIXME: Throw custom exception on failure
def migrate_repo(
    cloned_repo: ClonedRepo,
    repo_gitobj: GitRepo,
    migration: MigrationLoaded,
    logger: logging.Logger,
) -> tuple[PatchResult, Exception | None]:
    """Process a repo with Mass Driver"""
    try:
        migration.driver._logger = logging.getLogger(
            f"{logger.name}.driver.{migration.driver_name}"
        )
        result = migration.driver.run(cloned_repo)
    except Exception as e:
        result = PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details=f"Unhandled exception caught during patching. Error was: {e}",
        )
        return (result, e)
    logger.info(result.outcome.value)
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
