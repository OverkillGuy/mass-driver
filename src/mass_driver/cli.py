"""Command line entrypoint for mass-driver"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from mass_driver.drivers import Counter
from mass_driver.patch_driver import PatchDriver
from mass_driver.repo import clone_if_remote, commit


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
    )
    parser.add_argument(
        "repo-paths",
        nargs="*",
        help="List of Repositories to patch. If not local paths, will git clone them",
    )
    parser.add_argument(
        "--repo-filelist",
        type=argparse.FileType("r"),
        help="File with list of Repositories to Patch. If not local paths, will git clone them",
    )
    parser.add_argument(
        "--branch-name",
        help="Name of the patch branch. Defaults to the PatchDriver's classname",
    )
    detect_group = parser.add_mutually_exclusive_group()
    detect_group.add_argument(
        "--patch", action="store_true", help="Actually do the patching"
    )
    detect_group.add_argument(
        "--detect", action="store_true", help="Just detect, no patching"
    )
    parser.set_defaults(patch=False, detect=True)
    return parser.parse_args(arguments)


def cli(arguments: Optional[list[str]] = None):
    """Run the mass_driver cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    args = parse_arguments(arguments)
    if args.repo_filelist:
        args.repo_paths = args.repo_filelist.read().strip().split("\n")
    main(args.repo_paths, args.patch, args.branch_name)


def main(repo_paths: list[str], do_patch: bool, branch_name: Optional[str]):
    """Run the program's main command"""
    driver = Counter(counter_file=Path("counter"), target_count=1)
    if not branch_name:
        branch_name = driver.__class__.__name__.lower()
    repo_count = len(repo_paths)
    print(f"Processing {repo_count} with {driver=}")
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            process_repo(repo_path, driver, do_patch, branch_name)
        except Exception as e:
            print(
                f"Error processing repo '{repo_path}'\n" f"Error was: {e}",
                file=sys.stderr,
            )
            continue
    print("Action completed: exiting")


def process_repo(repo_path: str, driver: PatchDriver, do_patch: bool, branch_name: str):
    """Process a repo with Mass Driver: detect or patch"""
    repo = clone_if_remote(repo_path)
    if do_patch:
        print(f"Detecting '{repo_path}' before patching...")
        needs_patch = driver.detect(repo.working_dir)
        if not needs_patch:
            print("Does not need patching: skipping")
            return
        driver.patch(repo.working_dir)
        print("Done patching, committing")
        commit(repo, driver, branch_name)
        print("Done committing")
    else:
        needs_patch = driver.detect(repo.working_dir)
        print(f"Detecting '{repo_path}': {needs_patch=}")
