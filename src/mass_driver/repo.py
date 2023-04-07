"""Cloning remote repos (repos not using local path)"""

from pathlib import Path
from tempfile import mkdtemp

from git import Repo

from mass_driver.models.migration import MigrationLoaded

DEFAULT_CACHE = Path(".mass_driver/repos/")


def clone_if_remote(repo_path: str, cache_folder: Path) -> Repo:
    """Build a git Repo; If repo_path isn't a directory, clone it"""
    if Path(repo_path).is_dir():
        print("Given an existing (local) repo: no cloning")
        # Clone it into cache anyway
        return Repo(path=repo_path)  # FIXME: Actually clone-move the repo on the way.
    # SSH clone URL e.g: git@github.com:OverkillGuy/python-template
    if ":" in repo_path:  # Presence of : is proxy for SSH clone URL
        *_junk, repo_blurb = repo_path.split(":")
        org, repo_name = repo_blurb.split("/")
    else:
        org = "local"
        repo_name = Path(repo_path).name
    clone_target = cache_folder / org / repo_name
    if clone_target.is_dir():
        print("Given a URL for we cloned already: no cloning")
        return Repo(clone_target)
    print("Given a URL, cache miss: cloning")
    cloned = Repo.clone_from(
        url=repo_path,
        to_path=clone_target,
        multi_options=["--depth=1"],
    )
    return cloned


def get_cache_folder(cache: bool) -> Path:
    """Create a cache folder, either locally or in temp"""
    cache_folder = DEFAULT_CACHE
    if not cache:
        cache_folder = Path(mkdtemp(suffix=".cache"))
        print(f"Using repo cache folder: {cache_folder}/ (Won't wipe it on exit!)")
    return cache_folder


def commit(repo: Repo, migration: MigrationLoaded):
    """Commit the repo's changes in branch_name, given the PatchDriver that did it"""
    assert repo.is_dirty(untracked_files=True), "Repo shouldn't be clean on committing"
    branch = repo.create_head(migration.branch_name)
    branch.checkout()
    repo.git.add(A=True)
    author = None  # If stays None, git uses default commit author
    if migration.commit_author_email or migration.commit_author_name:
        name, email = migration.commit_author_name, migration.commit_author_email
        author = f"{name} <{email}>"  # Actor(name=migration.commit_author_name,
        #       email=migration.commit_author_email)
    repo.git.commit(m=migration.commit_message, author=author)


def push(repo: Repo, branch_name: str):
    """Push a branch of the repo to a remote"""
    remote = repo.remote()
    remote.push(refspec=branch_name)
