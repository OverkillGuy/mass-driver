"""Sample result objects, for analysis and summary"""

from pathlib import Path
from tempfile import mkdtemp

from mass_driver.models.activity import ActivityOutcome
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo, SourcedRepo
from mass_driver.models.status import Phase, RepoOutcome

PATCH_ERRORS = 1
ALREADY_PATCHED = 4
PATCH_DOES_NOT_APPLY = 5
PATCHED_OK = 12
PR_FAILED = 2
PR_CREATED = PATCHED_OK - PR_FAILED

SOURCED_COUNT = sum([PATCH_ERRORS, ALREADY_PATCHED, PATCH_DOES_NOT_APPLY, PATCHED_OK])


def generate_sample_results() -> ActivityOutcome:
    """Generate some sample results from multiple runs"""
    out = {
        f"repo-{i}": RepoOutcome(
            repo_id=f"repo-{i}",
            status=Phase.SOURCE,
            source=SourcedRepo(
                repo_id=f"repo-{i}", clone_url=f"git@example.com/repo-{i}.git"
            ),
        )
        for i in range(SOURCED_COUNT)
    }

    TMP_DIR = mkdtemp()

    tmp_subdirs = [
        Path(TMP_DIR) / f".mass_driver/repo-{i}" for i in range(SOURCED_COUNT)
    ]
    for subdir in tmp_subdirs:
        subdir.mkdir(parents=True)

    for i, tmp_subdir in enumerate(tmp_subdirs):
        repo_id = f"repo-{i}"
        out[repo_id].status = Phase.CLONE
        out[repo_id].clone = ClonedRepo(
            repo_id=repo_id,
            clone_url=f"git@example.com/repo-{i}.git",
            cloned_path=tmp_subdir,
            cloned_branch="main",
            current_branch="main",
        )

    migrated_outcomes = (
        ["PATCHED_OK"] * PATCHED_OK
        + ["ALREADY_PATCHED"] * ALREADY_PATCHED
        + ["PATCH_DOES_NOT_APPLY"] * PATCH_DOES_NOT_APPLY
        + ["PATCH_ERROR"] * PATCH_ERRORS
    )

    for i, outcome in enumerate(migrated_outcomes):
        repo_id = f"repo-{i}"
        out[repo_id].patch = PatchResult(outcome=PatchOutcome(outcome))
        out[repo_id].status = Phase.PATCH

    forge_outcomes = ["PR_FAILED"] * PR_FAILED + ["PR_CREATED"] * PR_CREATED

    for i, outcome in enumerate(forge_outcomes):
        repo_id = f"repo-{i}"
        out[repo_id].forge = PRResult(
            outcome=PROutcome(outcome),
            pr_html_url=f"https://example.com/repo-{i}/pulls/1"
            if outcome == "PR_CREATED"
            else None,
        )
        out[repo_id].status = Phase.FORGE

    return ActivityOutcome(repos=out)


SAMPLE_DATA = generate_sample_results()

# import logging
# import sys
# from mass_driver import summarize as s

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# logger = logging.getLogger("summary")


# s.summarize_source(SAMPLE_DATA.repos_sourced, logger)
# s.summarize_migration(SAMPLE_DATA.migration_result, logger,details=False)
# s.summarize_forge(SAMPLE_DATA.forge_result, logger,details=False)
