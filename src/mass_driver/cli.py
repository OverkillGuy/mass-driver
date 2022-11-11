"""Command line entrypoint for mass-driver"""
import argparse
import sys

from mass_driver.main import main


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
        epilog="Currently, only the simplistic 'Counter' Driver is set up",
    )
    repolist_group = parser.add_mutually_exclusive_group(required=True)
    repolist_group.add_argument(
        "--repo-paths",
        nargs="*",
        help="List of Repositories to patch. If not local paths, will git clone them",
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
    detect_group = parser.add_mutually_exclusive_group()
    detect_group.add_argument(
        "--patch", action="store_true", help="Actually do the patching"
    )
    detect_group.add_argument(
        "--detect", action="store_true", help="Just detect, no patching (default)"
    )
    parser.set_defaults(patch=False, detect=True)
    return parser.parse_args(arguments)


def cli(arguments: list[str] | None = None):
    """Run the mass_driver cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    args = parse_arguments(arguments)
    if args.repo_filelist:
        args.repo_paths = args.repo_filelist.read().strip().split("\n")
    main(args.repo_paths, args.patch, args.branch_name)
