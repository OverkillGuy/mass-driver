"""The main run-command of Forges, creating mass-PRs from existing branhces"""
from enum import Enum

from git import Repo
from pydantic import BaseModel

from mass_driver.migration import ForgeFile
from mass_driver.repo import push


def main(
    config: ForgeFile,
    repo_paths: list[str],
):
    """Process repo_paths with the given Forge"""
    repo_count = len(repo_paths)
    print(f"Processing {repo_count} with Forge...")
    pr_results = {}
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            result = process_repo(config, repo_path)
            pr_results[repo_path] = result
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            pr_results[repo_path] = PRResult(
                outcome=PROutcome.PR_FAILED,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            continue
    print("Action completed: exiting")
    return pr_results


def process_repo(
    config: ForgeFile,
    repo_path: str,
):
    """Process a single repo"""
    git_repo = Repo(path=repo_path)
    push(git_repo, config.head_branch)
    # Grab the repo's remote URL to feed it to the forge for ID
    (forge_remote_url,) = list(git_repo.remote().urls)
    pr = config.forge.create_pr(
        forge_repo_url=forge_remote_url,
        base_branch=config.base_branch,
        head_branch=config.head_branch,
        pr_title=config.pr_title,
        pr_body=config.pr_body,
        draft=config.draft_pr,
    )
    return PRResult(outcome=PROutcome.PR_CREATED, pr_html_url=pr)


class PROutcome(str, Enum):
    """The category of result after using a Forge over a single repository"""

    PR_CREATED = "PR_CREATED"
    """The PR was created correctly"""
    PR_FAILED = "PR_FAILED"
    """The PR failed to be created"""


class PRResult(BaseModel):
    """The result of applying a patch on a repo"""

    outcome: PROutcome
    """The kind of result that PR creation had"""
    pr_html_url: str | None = None
    """The HTML URL of the PR that was generated, if any"""
    details: str | None = None
    """Details of the PR creation of this repo, if any"""
