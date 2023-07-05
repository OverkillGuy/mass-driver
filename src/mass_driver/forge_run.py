"""The main run-command of Forges, creating mass-PRs from existing branhces"""

from git import Repo as GitRepo

from mass_driver.git import push
from mass_driver.models.activity import ActivityOutcome, IndexedPRResult
from mass_driver.models.forge import PROutcome, PRResult
from mass_driver.models.migration import ForgeLoaded
from mass_driver.models.repository import ClonedRepo


def main(
    config: ForgeLoaded,
    progress: ActivityOutcome,
) -> ActivityOutcome:
    """Process repo_paths with the given Forge"""
    repo_count = len(progress.repos_sourced)
    print(f"Processing {repo_count} with Forge...")
    pr_results: IndexedPRResult = {}
    for repo_index, (repo_id, repo) in enumerate(
        progress.repos_cloned.items(), start=1
    ):
        pause_every = config.interactive_pause_every
        if pause_every is not None and repo_index % pause_every == 0:
            pause_until_ok(f"Reached {pause_every} actions. Continue?\n")
        try:
            print(
                f"[{repo_index:03d}/{repo_count:03d}] Processing {repo.cloned_path}..."
            )
            result = process_repo(config, repo)
            pr_results[repo_id] = result
        except Exception as e:
            print(f"Error processing repo '{repo_id}'\nError was: {e}")
            pr_results[repo_id] = PRResult(
                outcome=PROutcome.PR_FAILED,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            continue
    print("Action completed: exiting")
    progress.forge_result = pr_results
    return progress


def process_repo(
    config: ForgeLoaded,
    repo: ClonedRepo,
) -> PRResult:
    """Process a single repo"""
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
            # FIXME: What to do with local URLs like in tests?
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


def get_default_branch(r: GitRepo) -> str:
    """Get the default branch of a repository"""
    # From https://github.com/gitpython-developers/GitPython/discussions/1364#discussioncomment-1530384
    try:
        return r.remotes.origin.refs.HEAD.ref.remote_head
    except Exception:
        raise ValueError(
            "base_branch param could not be autodetected: no git remote available"
        )


def pause_until_ok(message: str):
    """Halt until keyboard input is a variant of YES"""
    continue_asking = True
    while continue_asking:
        typed_text = input(message)
        if typed_text.lower() in ["y", "yes", "ok", "c", "continue"]:
            continue_asking = False
