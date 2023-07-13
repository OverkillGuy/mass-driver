"""Command line entrypoint for mass-driver"""
import sys
from argparse import ArgumentParser, FileType

# TODO: Check obsoleted-ness of Callable? See collections.abc.Callable?
from typing import Callable

from mass_driver import commands


def gen_parser() -> ArgumentParser:
    """Create the initial parser"""
    parser = ArgumentParser(
        "mass-driver",
        description="Send bulk repo change requests",
    )
    return parser


def repo_list_group(subparser: ArgumentParser):
    """Inject the repo-path/repo-filelist group of args"""
    repolist_group = subparser.add_mutually_exclusive_group(required=False)
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


def plugin_subparser(subparser, plugin: str, func: Callable):
    """Inject a generic subparser for listing out plugin details"""
    plugins = subparser.add_parser(
        f"{plugin}s",
        aliases=[plugin],
        help=f"Inspect {plugin}s (Plugins)",
    )
    plugins.add_argument(
        "--list", action="store_true", help=f"List available {plugin}s"
    )
    plugins.add_argument("--info", help=f"Show docs of a specific {plugin}")
    plugins.set_defaults(func=func)


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
    # "Scanners" are a little simpler than other plugins (func vs pydantic class)
    # Hence get their own smaller function, cannot reuse plugin_subparser
    scan = subparser.add_parser(
        "scanners",
        help="List available scanners",
    )
    scan.set_defaults(func=commands.scanners_command)


def reviewpr_subparser(subparser):
    """Inject the view PR subparser"""
    run = subparser.add_parser(
        "view-pr",
        help="Check status of given pull requests",
    )
    prlist_group = run.add_mutually_exclusive_group(required=True)
    prlist_group.add_argument(
        "--pr",
        nargs="*",
        help="One or more pull requests to review",
    )
    prlist_group.add_argument(
        "--pr-filelist",
        type=FileType("r"),
        help="File with list of pull requests",
    )
    run.add_argument(
        "forge", help="The name of the Forge plugin to use to look up status"
    )
    run.set_defaults(dry_run=True, func=commands.review_pr_command)


def subparsers(parser: ArgumentParser) -> ArgumentParser:
    """Add the subparsers for all commands"""
    subparser = parser.add_subparsers(dest="cmd", title="Commands")
    subparser.required = True
    plugin_subparser(subparser, "driver", commands.drivers_command)
    plugin_subparser(subparser, "forge", commands.forges_command)
    plugin_subparser(subparser, "source", commands.sources_command)
    run_subparser(subparser)
    scanners_subparser(subparser)
    reviewpr_subparser(subparser)
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
