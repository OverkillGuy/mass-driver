"""Per-repo processing of activities.

Given a single repo, process SINGLE "activity" (clone OR migrate OR scan OR forge).
"""

import logging
import traceback
from pathlib import Path

from mass_driver.git import (
    GitRepo,
    clone_if_remote,
    commit,
    get_default_branch,
    push,
    switch_branch_then_pull,
)
from mass_driver.models.activity import ScanResult
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.migration import ForgeLoaded, MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import (
    ClonedRepo,
    SourcedRepo,
)
from mass_driver.models.scan import ScanLoaded


def clone_repo(
    repo: SourcedRepo, logger: logging.Logger
) -> tuple[ClonedRepo, GitRepo]:
    """Clone a repo (if needed) and switch branch"""
    repo_gitobj = clone_if_remote(repo_path=repo.clone_url, logger=logger)
    switch_branch_then_pull(repo_gitobj, repo.force_pull, repo.upstream_branch)
    repo_local_path = Path(repo_gitobj.working_dir)
    cloned_repo = ClonedRepo(
        cloned_path=repo_local_path,
        current_branch=repo_gitobj.active_branch.name,
        **repo.dict(),
    )
    return cloned_repo, repo_gitobj


# TODO: Avoid passing out the exception, catch the trace in details kw (see scanner_run)
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
        return result, e
    logger.info(result.outcome.value)
    if result.outcome != PatchOutcome.PATCHED_OK:
        return result, None
    # Patched OK: Save the mutation
    commit(repo_gitobj, migration)
    return result, None


def scan_repo(config: ScanLoaded, cloned_repo: ClonedRepo) -> ScanResult:
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


def forge_per_repo(config: ForgeLoaded, repo: ClonedRepo) -> PRResult:
    """
    Run the forge
    :param config:
    :param repo:
    :return:
    """
    repo_path = repo.cloned_path
    if repo_path is None:
        raise ValueError("Repo not cloned locally, can't create PR of it")
    git_repo = GitRepo(path=str(repo_path))
    if config.git_push_first:
        push(git_repo, config.head_branch)
    # Grab the repo's remote URL to feed it to the forge for ID
    try:
        (forge_remote_url,) = list(git_repo.remote().urls)
    except ValueError:
        if not config.git_push_first:
            # No remote exists for repo and we didn't wanna push anyway
            # TODO: What to do with local URLs like in tests?
            forge_remote_url = (
                f"unix://{repo_path}"  # Pretending to have one and move on for tests
            )
    base_branch = (
        get_default_branch(git_repo)
        if config.base_branch is None
        else config.base_branch
    )
    pr = config.forge.create_pr(
        forge_repo_url=forge_remote_url,
        base_branch=base_branch,
        head_branch=config.head_branch,
        pr_title=config.pr_title,
        pr_body=config.pr_body,
        draft=config.draft_pr,
    )
    return PRResult(outcome=PROutcome.PR_CREATED, pr_html_url=pr)
