"""The main run-command of Forges, creating mass-PRs from existing branhces"""

import logging
from copy import deepcopy

from mass_driver.models.activity import ActivityOutcome
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.migration import ForgeLoaded
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.models.status import Error, Phase
from mass_driver.process_repo import forge_per_repo


def main(
    config: ForgeLoaded,
    progress: ActivityOutcome,
) -> ActivityOutcome:
    """Process repo_paths with the given Forge"""
    repos = [
        r
        for r in progress.repos.values()
        if r.status == Phase.PATCH
        and r.patch is not None
        and r.patch.outcome == PatchOutcome.PATCHED_OK
    ]
    out = deepcopy(progress.repos)
    repo_count = len(repos)
    logging.info(f"Processing {repo_count} with Forge...")
    for repo_index, repo in enumerate(repos, start=1):
        repo_id = repo.repo_id
        pause_every = config.interactive_pause_every
        if pause_every is not None and repo_index % pause_every == 0:
            pause_until_ok(f"Reached {pause_every} actions. Continue?\n")
        try:
            out[repo_id].status = Phase.FORGE
            repo_clone = repo.clone
            if repo_clone is None:
                raise ValueError("No clone data for this forge request")
            logging.info(
                f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_clone.cloned_path}..."
            )
            result = forge_per_repo(config, repo_clone)
            out[repo_id].forge = result
        except Exception as e:
            logging.error(f"Error processing repo '{repo_id}'")
            logging.exception(e)
            error = Error.from_exception(activity=Phase.FORGE, exception=e)
            out[repo_id].forge = PRResult(
                outcome=PROutcome.PR_FAILED,
                details="Unhandled exception caught during Forge",
                error=error,
            )
            out[repo_id].error = error
    logging.info("Action completed: exiting")
    return ActivityOutcome(repos=out)


def pause_until_ok(message: str):
    """Halt until keyboard input is a variant of YES"""
    continue_asking = True
    while continue_asking:
        typed_text = input(message)
        if typed_text.lower() in ["y", "yes", "ok", "c", "continue"]:
            continue_asking = False
