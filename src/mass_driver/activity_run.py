"""Main activities of Mass-Driver: For each repo, clone it, then scan/migrate it

Variants for sequential or parallel
"""

import logging
from concurrent import futures
from copy import deepcopy

from mass_driver.git import (
    get_cache_folder,
)
from mass_driver.models.activity import (
    ActivityLoaded,
    ActivityOutcome,
)
from mass_driver.models.outcome import RepoOutcome
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.status import Error, Phase
from mass_driver.process_repo import clone_repo, migrate_repo, scan_repo

LOGGER_PREFIX = "run"


def sequential_run(
    activity: ActivityLoaded,
    reps: ActivityOutcome,
    cache: bool,
) -> ActivityOutcome:
    """Run the main activity SEQUENTIALLY: over N repos, clone, then scan/patch"""
    logger = logging.getLogger(LOGGER_PREFIX)
    repos = reps.repos
    repo_count = len(repos.keys())
    out = deepcopy(repos)
    migration = activity.migration
    scan = activity.scan
    cache_folder = get_cache_folder(cache, logger=logger)
    what_array = ["clone"]
    if scan is not None:
        what_array.append(f"{len(scan.scanners)} scanners")
    if migration is not None:
        what_array.append(f"{migration.driver=}")
    logger.info(f"Processing {repo_count} with {' and '.join(what_array)}")
    for repo_index, (repo_id, repo) in enumerate(repos.items(), start=1):
        repo_logger_name = f"{logger.name}.repo.{repo_id.replace('.','_')}"
        repo_logger = logging.getLogger(repo_logger_name)
        try:
            logger.info(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_id}...")
            cloned_repo, repo_gitobj = clone_repo(
                repo.source, cache_folder, logger=repo_logger
            )
            out[repo_id].clone = cloned_repo
            out[repo_id].status = Phase.CLONE
        except Exception as e:
            repo_logger.error("Error while cloning the repo")
            repo_logger.exception(e)
            out[repo_id].clone = None
            out[repo_id].status = Phase.CLONE
            out[repo_id].error = Error.from_exception(activity=Phase.CLONE, exception=e)
            continue
        # Clone was OK, proceed:
        if scan:
            # We mean to scan now...
            out[repo_id].status = Phase.SCAN
            if out[repo_id].error is None:  # Only scan if no error before
                out[repo_id].scan = scan_repo(scan, cloned_repo)
        if migration:
            # We mean to patch now...
            out[repo_id].status = Phase.PATCH
            error = out[repo_id].error
            if error is not None:
                # Error in pre-requisite: skip patching, forwarding the (cloning?) error
                out[repo_id].patch = PatchResult(
                    outcome=PatchOutcome.PATCH_ERROR,
                    details="Uncaught error before we got to patching",
                    error=error,
                )
                continue  # Skip the actual patching due to error
            # Properly patch now
            try:
                # Ensure no driver persistence between repos
                migration_copy = deepcopy(migration)
                out[repo_id].patch = migrate_repo(
                    cloned_repo, repo_gitobj, migration_copy, logger=repo_logger
                )
            except Exception as e:
                repo_logger.error("Migration error")
                repo_logger.exception(e)
                error = Error.from_exception(activity=Phase.PATCH, exception=e)
                out[repo_id].patch = PatchResult(
                    outcome=PatchOutcome.PATCH_ERROR,
                    details="Unhandled exception caught during patching",
                    error=error,
                )
                out[repo_id].status = Phase.PATCH
                out[repo_id].error = error
    logger.info("Action completed: exiting")
    return ActivityOutcome(repos=out)


def thread_run(
    activity: ActivityLoaded,
    rep: ActivityOutcome,
    cache: bool,
) -> ActivityOutcome:
    """Run the main activity THREADED: over N repos, clone, then scan/patch"""
    logger = logging.getLogger(LOGGER_PREFIX)
    repos = rep.repos
    out = deepcopy(repos)
    repo_count = len(repos.keys())
    migration = activity.migration
    scan = activity.scan
    cache_folder = get_cache_folder(cache, logger=logger)
    what_array = ["clone"]
    if scan is not None:
        what_array.append(f"{len(scan.scanners)} scanners")
    if migration is not None:
        what_array.append(f"{migration.driver=}")

    logger.info(f"Processing {repo_count} with {' and '.join(what_array)}, via Threads")
    futures_map = {}
    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        for repo_id, repo in repos.items():
            future_obj = executor.submit(
                per_repo_process,
                repo_id,
                repo,
                activity,
                logging.getLogger(f"{logger.name}.repo.{repo_id.replace('.','_')}"),
                cache_folder,
            )
            futures_map[future_obj] = repo_id
        # Submitted the jobs: iterate on completion
        for repo_index, future in enumerate(futures.as_completed(futures_map), start=1):
            logger.info(f"[{repo_index:04d}/{repo_count:04d}] Processed {repo_id}")
            repo_id = futures_map[future]
            out[repo_id] = future.result()
            logger.info("Action completed: exiting")
    return ActivityOutcome(repos=out)


def per_repo_process(repo_id, repo, activity, logger, cache_folder) -> RepoOutcome:
    """Process a single repo, in-thread"""
    out = deepcopy(repo)
    try:
        cloned_repo, repo_gitobj = clone_repo(repo.source, cache_folder, logger=logger)
        out.clone = cloned_repo
        out.status = Phase.CLONE
    except Exception as e:
        logger.error("Error while cloning the repo")
        logger.exception(e)
        out.clone = None
        out.status = Phase.CLONE
        out.error = Error.from_exception(activity=Phase.CLONE, exception=e)
    # Clone was OK, proceed:
    if activity.scan:
        # We mean to scan now...
        out.status = Phase.SCAN
        if out.error is None:  # Only scan if no error before
            out.scan = scan_repo(activity.scan, cloned_repo)
    if not activity.migration:
        return out
    # We mean to patch now...
    out.status = Phase.PATCH
    error = out.error
    if error is not None:
        # Error in pre-requisite: skip patching, forwarding the (cloning?) error
        out.patch = PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details="Uncaught error before we got to patching",
            error=error,
        )
    # Properly patch now
    try:
        # Ensure no driver persistence between repos
        migration_copy = deepcopy(activity.migration)
        out.patch = migrate_repo(
            cloned_repo, repo_gitobj, migration_copy, logger=logger
        )
    except Exception as e:
        logger.error("Migration error")
        logger.exception(e)
        error = Error.from_exception(activity=Phase.PATCH, exception=e)
        out.patch = PatchResult(
            outcome=PatchOutcome.PATCH_ERROR,
            details="Unhandled exception caught during patching",
            error=error,
        )
        out[repo_id].status = Phase.PATCH
        out[repo_id].error = error
    return out
