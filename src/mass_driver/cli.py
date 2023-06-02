"""Command line entrypoint for mass-driver"""
import sys
from argparse import ArgumentParser, FileType

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


def repo_list_group(subparser: ArgumentParser):
    """Inject the repo-path/repo-filelist group of args"""
    repolist_group = subparser.add_mutually_exclusive_group(required=True)
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


def cache_arg(subparser: ArgumentParser):
    """Add the cache/no-cache arguments"""
    subparser.add_argument(
        "--no-cache",
        help="Disable any repo caching",
        action="store_true",
    )


def activity_arg(subparser: ArgumentParser):
    """Add the Activity file selector argument"""
    subparser.add_argument(
        "activity_file",
        help="Filepath of activity to apply (TOML file)",
        type=FileType("r"),
    )


def jsonout_args(subparser: ArgumentParser):
    """Add the output files argument"""
    subparser.add_argument(
        "--json-outfile",
        help="If set, store the output to JSON file with this name",
        type=FileType("w"),
    )


def driver_subparser(subparser):
    """Inject the drivers-listing argument subparser"""
    drivers = subparser.add_parser(
        "drivers",
        aliases=["driver"],
        help="Inspect drivers (Plugins)",
    )
    drivers.add_argument("--list", action="store_true", help="List available drivers")
    drivers.add_argument("--info", help="Show docs of a specific driver")
    drivers.set_defaults(func=commands.drivers_command)


def forge_subparser(subparser):
    """Inject the forge-listing subparser"""
    forges = subparser.add_parser(
        "forges",
        aliases=["forge"],
        help="Inspect forges (Plugins)",
    )
    forges.add_argument("--list", action="store_true", help="List available forges")
    forges.add_argument("--info", help="Show docs of a specific forge")
    forges.set_defaults(func=commands.forges_command)


def run_subparser(subparser):
    """Inject the run subparser"""
    run = subparser.add_parser(
        "run",
        help="Run mass-driver, migration/forge activity across repos",
    )
    activity_arg(run)
    jsonout_args(run)
    run.add_argument(
        "--no-pause",
        help="Disable the interactive pause between Migration and Forge",
        action="store_true",
    )
    cache_arg(run)
    repo_list_group(run)
    run.set_defaults(dry_run=True, func=commands.run_command)


def scanners_subparser(subparser):
    """Inject the scanners subparser"""
    scan = subparser.add_parser(
        "scanners",
        help="List available scanners",
    )
    scan.set_defaults(func=commands.scanners_command)


def scan_subparser(subparser):
    """Inject the scan subparser"""
    scan = subparser.add_parser(
        "scan",
        help="Scan repositories using all available scans",
    )
    activity_arg(scan)
    jsonout_args(scan)
    repo_list_group(scan)
    cache_arg(scan)
    scan.set_defaults(func=commands.scan_command)


def subparsers(parser: ArgumentParser) -> ArgumentParser:
    """Add the subparsers for all commands"""
    subparser = parser.add_subparsers(dest="cmd", title="Commands")
    subparser.required = True
    driver_subparser(subparser)
    forge_subparser(subparser)
    run_subparser(subparser)
    scanners_subparser(subparser)
    scan_subparser(subparser)
    return parser


def cli(arguments: list[str]):
    """Run the mass_driver cli"""
    parser = subparsers(gen_parser())
    pargs = parser.parse_args(arguments)
    try:
        return pargs.func(pargs)  # Dispatch to the subcommand func (drivers/run)
    except Exception as e:
        print(f"Uncaught exception: {e}", file=sys.stderr)
        return False


def main():
    """Run mass-driver as CLI, not from API call"""
    arguments = sys.argv[1:]
    main_result = cli(arguments)
    return 0 if main_result else 1
