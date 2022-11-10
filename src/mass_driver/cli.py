"""Command line entrypoint for mass-driver"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from mass_driver.drivers import Counter


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
    )
    parser.add_argument(
        "repo_path", help="Repository to Patch. If not a local path, will git clone it"
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
    repo_path = Path(args.repo_path)
    main(repo_path, args.patch)


def main(repo_path: Path, do_patch: bool):
    """Run the program's main command"""
    driver = Counter(counter_file=Path("counter"), target_count=1)
    if do_patch:
        print(f"Patching '{repo_path}'...")
        driver.patch(repo_path)
    else:
        needs_patch = driver.detect(repo_path)
        print(f"Detecting '{repo_path}': {needs_patch=}")
