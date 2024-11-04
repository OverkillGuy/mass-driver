"""Sample result objects, for analysis and summary"""

from mass_driver.models.activity import ActivityOutcome
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.outcome import RepoOutcome
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.models.repository import ClonedRepo, SourcedRepo
from mass_driver.models.status import Error, Phase

SOURCED = 5
CLONE_ERROR = 5
PATCH_ERROR_CLONE_ERROR = 5
PATCH_ERRORS = 1
PATCHED_OK = 12
FORGE_ERROR_CLONE_ERROR = 5
FORGE_ERROR_PATCH_ERROR = 5
FORGE_ERROR = 5
FORGE_OK = 5


BAD_CLONE = Error.from_exception(
    activity=Phase.CLONE, exception=ValueError("Clone bad")
)
BAD_PATCH = Error.from_exception(
    activity=Phase.PATCH, exception=ValueError("Patch bad")
)
BAD_FORGE = Error.from_exception(
    activity=Phase.FORGE, exception=ValueError("Forge bad")
)


def generate() -> ActivityOutcome:
    """Generate sample data based on sample results"""
    out = {}

    acc = 1
    for i in range(acc, acc + SOURCED + 1):
        repo_id = f"repo-{i}"
        repo = generate_sourced(repo_id)
        out[repo_id] = repo
    acc += SOURCED

    for i in range(acc, acc + CLONE_ERROR + 1):
        repo_id = f"repo-{i}"
        repo = clone_error(generate_sourced(repo_id))
        out[repo_id] = repo
    acc += CLONE_ERROR
    for i in range(acc, acc + PATCH_ERROR_CLONE_ERROR + 1):
        repo_id = f"repo-{i}"
        repo = patch_error_from_clone(generate_sourced(repo_id))
        out[repo_id] = repo
    acc += PATCH_ERROR_CLONE_ERROR
    for i in range(acc, acc + PATCH_ERRORS + 1):
        repo_id = f"repo-{i}"
        repo = patch_error_during_patch(clone_ok(generate_sourced(repo_id)))
        out[repo_id] = repo
    acc += PATCH_ERRORS
    for i in range(acc, acc + PATCHED_OK + 1):
        repo_id = f"repo-{i}"
        repo = patch_ok(clone_ok(generate_sourced(repo_id)))
        out[repo_id] = repo
    acc += PATCHED_OK
    for i in range(acc, acc + FORGE_ERROR_CLONE_ERROR + 1):
        repo_id = f"repo-{i}"
        repo = forge_error_from_clone(patch_error_from_clone(generate_sourced(repo_id)))
        out[repo_id] = repo
    acc += FORGE_ERROR_CLONE_ERROR
    for i in range(acc, acc + FORGE_ERROR_PATCH_ERROR + 1):
        repo_id = f"repo-{i}"
        repo = forge_error_from_patch(
            patch_error_during_patch(clone_ok(generate_sourced(repo_id)))
        )
        out[repo_id] = repo
    acc += FORGE_ERROR_PATCH_ERROR
    for i in range(acc, acc + FORGE_ERROR + 1):
        repo_id = f"repo-{i}"
        repo = forge_error_during_forge(patch_ok(clone_ok(generate_sourced(repo_id))))
        out[repo_id] = repo
    acc += FORGE_ERROR
    for i in range(acc, acc + FORGE_OK + 1):
        repo_id = f"repo-{i}"
        repo = forge_ok(patch_ok(clone_ok(generate_sourced(repo_id))))
        out[repo_id] = repo
    acc += FORGE_OK
    return ActivityOutcome(repos=out)


def generate_sourced(repo_id: str) -> RepoOutcome:
    """Generate a single Sourced repo"""
    return RepoOutcome(
        repo_id=repo_id,
        status=Phase.SOURCE,
        source=SourcedRepo(repo_id=repo_id, clone_url=f"git@example.com/{repo_id}.git"),
    )


def patch_ok(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Cloned repo into a Patch OK"""
    assert repo.error is None, "Shouldn't have error before patch-ok"
    repo.status = Phase.PATCH
    repo.patch = PatchResult(outcome=PatchOutcome.PATCHED_OK)
    return repo


def forge_ok(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single PatchedOk repo into a Forge OK"""
    assert repo.error is None, "Shouldn't have error before forge-ok"
    repo.status = Phase.FORGE
    repo.forge = PRResult(
        outcome=PROutcome.PR_CREATED,
        pr_html_url=f"https://github.com/{repo.repo_id}/pull/1",
    )
    return repo


def clone_ok(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Sourced repo to be Cloned OK"""
    repo_path = "/tmp/" + repo.repo_id
    repo.status = Phase.CLONE
    repo.clone = ClonedRepo(
        cloned_path=repo_path,
        current_branch="main",
        commit_hash=("0" * 40),
        **repo.source.model_dump(),
    )
    return repo


def clone_error(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Sourced repo to be a Clone error"""
    repo.status = Phase.CLONE
    repo.error = BAD_CLONE
    return repo


def patch_error(repo: RepoOutcome, error: Error) -> RepoOutcome:
    """Tweak a single Repo (whatever it was) into a post-Patch error, given the error"""
    repo.error = error
    repo.status = Phase.PATCH
    repo.patch = PatchResult(outcome=PatchOutcome.PATCH_ERROR, error=error)
    return repo


def forge_error(repo: RepoOutcome, error: Error) -> RepoOutcome:
    """Tweak a single Repo (whatever it was) into a post-Forge error, given the error"""
    repo.error = error
    repo.status = Phase.FORGE
    repo.forge = PRResult(outcome=PROutcome.PR_FAILED, error=error)
    return repo


def patch_error_from_clone(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Cloned repo into a post-Patch error due to bad clone"""
    return patch_error(repo, BAD_CLONE)


def patch_error_during_patch(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Cloned repo into a post-Patch error due to bad patch"""
    return patch_error(repo, BAD_PATCH)


def forge_error_from_clone(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Sourced repo into a post-Forge error due to bad clone"""
    return forge_error(repo, BAD_CLONE)


def forge_error_from_patch(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Sourced repo into a post-Forge error due to bad patch"""
    return forge_error(repo, BAD_PATCH)


def forge_error_during_forge(repo: RepoOutcome) -> RepoOutcome:
    """Tweak a single Sourced repo into a post-Forge error due to bad forge"""
    return forge_error(repo, BAD_FORGE)


SAMPLE_DATA = generate()
# import logging
# import sys

# from mass_driver import summarize as s
# from mass_driver.summarize import explain

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# logger = logging.getLogger("summary")


# explain(SAMPLE_DATA.repos["repo-1"], logger)
# s.summarize_source(SAMPLE_DATA, logger)
# s.summarize_migration(SAMPLE_DATA, logger, details=False)
# s.summarize_forge(SAMPLE_DATA, logger, details=False)
