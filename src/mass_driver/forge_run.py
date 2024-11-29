"""The main run-command of Forges, creating mass-PRs from existing branhces"""
import logging

from mass_driver.models.activity import ActivityOutcome, IndexedPRResult
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.migration import ForgeLoaded
from mass_driver.process_repo import forge_per_repo


def main(
    config: ForgeLoaded,
    progress: ActivityOutcome,
) -> ActivityOutcome:
    """Process repo_paths with the given Forge"""
    repo_count = len(progress.repos_sourced)
    logging.info(f"Processing {repo_count} with Forge...")
    pr_results: IndexedPRResult = {}
    for repo_index, (repo_id, repo) in enumerate(
        progress.repos_cloned.items(), start=1
    ):
        pause_every = config.interactive_pause_every
        if pause_every is not None and repo_index % pause_every == 0:
            pause_until_ok(f"Reached {pause_every} actions. Continue?\n")
        try:
            logging.info(
                f"[{repo_index:03d}/{repo_count:03d}] Processing {repo.cloned_path}..."
            )
            result = forge_per_repo(config, repo)
            pr_results[repo_id] = result
        except Exception as e:
            logging.error(f"Error processing repo '{repo_id}'")
            logging.error(f"Error was: {e}")
            pr_results[repo_id] = PRResult(
                outcome=PROutcome.PR_FAILED,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            continue
    logging.info("Action completed: exiting")
    progress.forge_result = pr_results
    return progress


def pause_until_ok(message: str):
    """Halt until keyboard input is a variant of YES"""
    while True:
        if input(message).lower() in ["y", "ye", "yes", "ok", "c", "continue"]:
            break
