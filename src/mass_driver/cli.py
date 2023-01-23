"""Command line entrypoint for mass-driver"""
import sys
from argparse import ArgumentParser, FileType, Namespace

from mass_driver import commands


def gen_parser() -> ArgumentParser:
    """Create the initial parser"""
    parser = ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
    )
    # parser.add_argument(
    #     "--token-file",
    #     help="File containing Github API Token",
    #     type=argparse.FileType("r"),
    # )
    return parser


def subparsers(parser: ArgumentParser) -> ArgumentParser:
    """Add subparsers for driver selection"""
    subparser = parser.add_subparsers(dest="cmd", title="Commands")
    subparser.required = True
    drivers = subparser.add_parser(
        "drivers",
        aliases=["driver"],
        help="Inspect drivers (Plugins)",
    )
    drivers.add_argument("--list", action="store_true", help="List available drivers")
    drivers.add_argument("--info", help="Show docs of a specific driver")
    drivers.set_defaults(func=commands.drivers_command)
    run = subparser.add_parser(
        "run",
        help="Run mass-driver over multiple repos",
        epilog="Github API token requires either --token-file flag or envvar GITHUB_API_TOKEN\nCurrently no driver selection",
    )
    run.add_argument(
        "migration_file",
        help="Filepath of migration-config to apply (TOML file)",
        type=FileType("r"),
    )
    run.add_argument(
        "--no-cache",
        help="Disable any repo caching",
        action="store_true",
    )
    detect_group = run.add_mutually_exclusive_group()
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
    run.set_defaults(dry_run=True, func=commands.run_command)
    repolist_group = run.add_mutually_exclusive_group(required=True)
    repolist_group.add_argument(
        "--repo-path",
        nargs="*",
        help="One or more Repositories to patch. If not local paths, will git clone them",
    )
    repolist_group.add_argument(
        "--repo-filelist",
        type=FileType("r"),
        help="File with list of Repositories to Patch. If not local paths, will git clone them",
    )
    return parser


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse generic arguments, given as parameters"""
    parser = subparsers(gen_parser())
    return parser.parse_args(arguments)


def cli(arguments: list[str] | None = None):
    """Run the mass_driver cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    pargs = parse_arguments(arguments)
    return pargs.func(pargs)  # Dispatch to the subcommand func (drivers/run)
