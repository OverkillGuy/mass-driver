"""Summarize the result of a run, even a previous one"""
from collections import defaultdict
from logging import Logger

from mass_driver.models.activity import (
    ActivityOutcome,
)
from mass_driver.models.forge import PROutcome
from mass_driver.models.outcome import RepoOutcome
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.models.status import Phase


def group_by_outcome(result):
    """Group a result by its outcome"""
    # TODO: Consider using groupby instead
    repo_by_type = defaultdict(list)
    for _junk, repo_result in result.items():
        repo_by_type[repo_result.outcome].append(repo_result)
    return repo_by_type


def summarize_source(result: ActivityOutcome, logger: Logger):
    """Summarize Source result"""
    repos_sourced = [
        repo for repo in result.repos.values() if repo.status == Phase.SOURCE
    ]
    logger.info(f"Source results: discovered {len(repos_sourced)} repos")


def summarize_migration(result: ActivityOutcome, logger: Logger, details: bool = True):
    """Summarize migration result"""
    patched = [
        (repo.repo_id, repo.patch)
        for repo in result.repos.values()
        if repo.patch is not None
    ]
    repos_by_outcome = defaultdict(list)
    for repo_id, repo_result in patched:
        repos_by_outcome[repo_result.outcome].append(repo_id)
    summarize_result(repos_by_outcome, "migration", logger)
    if details:
        print_migration(repos_by_outcome, logger)


def summarize_forge(result: ActivityOutcome, logger: Logger, details: bool = True):
    """Summarize forge result"""
    forged = [repo for repo in result.repos.values() if repo.forge is not None]
    repos_by_outcome = defaultdict(list)
    for repo_result in forged:
        assert repo_result.forge is not None, "Should have gotten only forged repos"
        repos_by_outcome[repo_result.forge.outcome].append(repo_result.repo_id)
    summarize_result(repos_by_outcome, "forge", logger)
    print_prs(result, logger)
    if details:
        print_forge(repos_by_outcome, logger)


def print_prs(result: ActivityOutcome, logger: Logger):
    """Print the list of PRs created"""
    success_prs = []
    forged = [repo.forge for repo in result.repos.values() if repo.forge is not None]
    for f in forged:
        if f.outcome == PROutcome.PR_CREATED and f.pr_html_url is not None:
            success_prs.append(f.pr_html_url)
    logger.info(f"{len(success_prs)} PRs created:")
    for repo in sorted(success_prs):
        logger.info(repo)


def summarize_result(repos_by_outcome, activity_name, logger: Logger):
    """Summarize results, whatever group they are in"""
    total = sum(len(repo_by_outcome) for repo_by_outcome in repos_by_outcome.values())
    count_by_outcome = {
        outcome: len(repos) for outcome, repos in repos_by_outcome.items()
    }
    count_desc_by_outcome = {
        k.value: v
        for k, v in sorted(count_by_outcome.items(), key=lambda kv: kv[1], reverse=True)
    }

    logger.info(f"{activity_name.capitalize()} results:")
    logger.info(f"{total} repos processed, of which...")
    for outcome, count in count_desc_by_outcome.items():
        if count:
            status_percent = (float(count) / total) * 100
            logger.info(f"- {count:03} ({status_percent:04.2f}%) {outcome}")


def print_migration(repos_by_outcome, logger: Logger):
    """Print each repo by result type"""
    # Sort by DESC number of repo with outcome
    repos_desc_by_outcome = {
        k.value: v
        for k, v in sorted(
            repos_by_outcome.items(), key=lambda kv: len(kv[1]), reverse=True
        )
    }
    if repos_desc_by_outcome:
        logger.info("Now, repo list grouped by migration outcome")
    for outcome, repos in repos_desc_by_outcome.items():
        logger.info(f"For {outcome}:")
        for repo in sorted(repos):
            logger.info(repo)


def print_forge(repos_by_outcome, logger: Logger):
    """Print each repo by result type"""
    # Sort by DESC number of repo with outcome
    repos_desc_by_outcome = {
        k.value: v
        for k, v in sorted(
            repos_by_outcome.items(), key=lambda kv: len(kv[1]), reverse=True
        )
    }
    if repos_desc_by_outcome:
        logger.info("Now, repo list grouped by forge outcome")
    for outcome, repos in repos_desc_by_outcome.items():
        logger.info(f"For {outcome}:")
        for repo in sorted(repos):
            logger.info(repo)


def explain(repo: RepoOutcome, logger: Logger):
    """Explain a single result repository"""
    logger.info(f"Detailed results for repo ID '{repo.repo_id}'...")
    logger.info(f"Latest phase: '{repo.status.value}'")
    if repo.error is None:
        logger.info("No overall error logged")
    else:
        error = repo.error
        logger.info(
            f"Overall error signaled! Error was at phase: {error.activity.value}"
        )
    if not repo.clone:
        logger.info("No clone activity attempted")
    elif repo.clone is not None and repo.clone.error is None:
        logger.info(f"Cloned OK, to path {repo.clone.cloned_path}")
    elif repo.clone is not None and repo.clone.error is not None:
        logger.info(f"Clone failure, error was: {repo.clone.error}")
    if not repo.patch:
        logger.info("No patch activity attempted")
    elif repo.patch:
        patch = repo.patch
        logger.info(f"Proceeded to Patch, with outcome {patch.outcome.value}")
        if patch.outcome == PatchOutcome.PATCH_ERROR and patch.error is not None:
            # An error: from now or previous phase?
            error = patch.error
            if error.activity == Phase.PATCH:
                logger.info(f"Error was: {error}")
            else:
                logger.info(
                    f"Error is cascaded from previous phase {error.activity.value}"
                )
    if repo.scan:
        # FIXME: Update when Scan contains error
        logger.info(f"Scanned OK, with {len(repo.scan.keys())} scanners")
    elif not repo.scan:
        logger.info("No scan activity attempted")
    if not repo.forge:
        logger.info("No forge activity attempted")
    elif repo.forge:
        forge = repo.forge
        logger.info(f"Proceeded to Forge, with outcome {forge.outcome.value}")
        if forge.outcome == PROutcome.PR_FAILED and forge.error is not None:
            # An error: from now or previous phase?
            error = forge.error
            if error.activity == Phase.FORGE:
                logger.info(f"Error was: {error}")
            else:
                logger.info(
                    f"Error is cascaded from previous phase {error.activity.value}"
                )
