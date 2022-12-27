"""Command line entrypoint for mass-driver"""
import argparse
import os
import sys
from pathlib import Path

from mass_driver.discovery import discover_drivers, load_drivers
from mass_driver.main import main


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
        epilog="Github API token requires either --token-file flag or envvar GITHUB_API_TOKEN\nCurrently no driver selection",
    )
    repolist_group = parser.add_mutually_exclusive_group(required=True)
    repolist_group.add_argument(
        "--repo-path",
        nargs="*",
        help="One or more Repositories to patch. If not local paths, will git clone them",
    )
    repolist_group.add_argument(
        "--repo-filelist",
        type=argparse.FileType("r"),
        help="File with list of Repositories to Patch. If not local paths, will git clone them",
    )
    parser.add_argument(
        "--branch-name",
        help="Name of the patch branch. Defaults to the PatchDriver's classname",
    )
    parser.add_argument(
        "driver",
        help="Name of the driver to use",
    )
    detect_group = parser.add_mutually_exclusive_group()
    detect_group.add_argument(
        "--really-commit-changes",
        dest="dry_run",
        action="store_false",
        help="Really commit changes (locally, no pushing)",
    )
    detect_group.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Dry run, no actual commit, no pushing (default)",
    )
    parser.set_defaults(dry_run=True)
    parser.add_argument(
        "--token-file",
        help="File containing Github API Token",
        type=argparse.FileType("r"),
    )
    return parser.parse_args(arguments)


def cli(arguments: list[str] | None = None):
    """Run the mass_driver cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    args = parse_arguments(arguments)
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    token = get_token(args)
    driver_class = get_driver(args.driver)
    driver_instance = driver_class(
        target_file=Path("test.json"), **{"op": "add", "path": "/foo", "value": "bar"}
    )
    main(driver_instance, args.repo_path, args.dry_run, args.branch_name, token)


def get_token(args) -> str:
    """Grab the Forge API Token one way or the other"""
    if args.token_file:
        token = args.token_file.read().strip()
    else:
        token = os.getenv("GITHUB_API_TOKEN")
    if token is None:
        print(
            "Missing API token: --token-file or set GITHUB_API_TOKEN envvar",
            file=sys.stderr,
        )
        exit(2)  # Simulate the argparse behaviour of exiting on bad args
    return token


def get_driver(driver_name: str):
    """Fetch the given driver, by name"""
    discovered = discover_drivers()
    drivers = load_drivers(discovered)
    if driver_name not in drivers:
        raise ImportError("Driver not found")
    return drivers[driver_name]
