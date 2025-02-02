"""Main activities of Mass-Driver: For each repo, clone it, then scan/migrate it

Variants for sequential or parallel
"""

import logging
import os
from concurrent import futures
from copy import deepcopy

from mass_driver.models.activity import (
    ActivityLoaded,
    ActivityOutcome,
    IndexedPatchResult,
    IndexedScanResult,
    ScanResult,
)
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import (
    IndexedClonedRepos,
    IndexedRepos,
)
from mass_driver.process_repo import clone_repo, migrate_repo, scan_repo

LOGGER_PREFIX = "run"


def thread_run(activity: ActivityLoaded, repos: IndexedRepos) -> ActivityOutcome:
    """Run the main activity THREADED: over N repos, clone, then scan/patch"""
    logger = logging.getLogger(LOGGER_PREFIX)
    repo_count = len(repos.keys())
    migration = activity.migration
    scan = activity.scan
    cloned_repos: IndexedClonedRepos = {}
    scanner_results: IndexedScanResult | None = None
    patch_results: IndexedPatchResult | None = None
    what_array = ["clone"]
    if scan is not None:
        what_array.append(f"{len(scan.scanners)} scanners")
        scanner_results = {}
    if migration is not None:
        what_array.append(f"{migration.driver=}")
        patch_results = {}

    logger.info(f"Processing {repo_count} with {' and '.join(what_array)}, via Threads")

    futures_map = {}
    with futures.ThreadPoolExecutor(max_workers=int(os.environ.get("MASS_DRIVER_THREADS", 8))) as executor:
        for repo_id, repo in repos.items():
            future_obj = executor.submit(
                per_repo_process,
                repo_id,
                repo,
                activity,
                logging.getLogger(f"{logger.name}.repo.{repo_id.replace('.','_')}"))
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


def per_repo_process(repo_id, repo, activity, logger):
    """Process a single repo, in-thread"""
    try:
        logger.info(f"Processing {repo_id}...")
        cloned_repo, repo_gitobj = clone_repo(repo, logger=logger)
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
    return cloned_repo, scan_result, patch_result
