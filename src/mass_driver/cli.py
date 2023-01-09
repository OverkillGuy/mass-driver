"""Command line entrypoint for mass-driver"""
import os
import sys
from argparse import ArgumentParser, FileType, Namespace

from mass_driver.discovery import driver_from_config
from mass_driver.main import main


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
        help="Inspect drivers (Plugins)",
    )
    drivers.add_argument("--list", action="store_true", help="List available drivers")
    drivers.add_argument("--info", help="Show docs of a specific driver")
    drivers.set_defaults(func=drivers_command)
    run = subparser.add_parser(
        "run",
        help="Run mass-driver over multiple repos",
        epilog="Github API token requires either --token-file flag or envvar GITHUB_API_TOKEN\nCurrently no driver selection",
    )
    run.add_argument(
        "--driver-config",
        help="Config of driver to apply (TOML)",
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
    run.set_defaults(dry_run=True, func=run_command)
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
    run.add_argument(
        "--branch-name",
        help="Name of the patch branch. Defaults to the PatchDriver's classname",
    )
    return parser


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse generic arguments, given as parameters"""
    parser = subparsers(gen_parser())
    return parser.parse_args(arguments)


def drivers_command(args: Namespace):
    """Process the CLI for 'Drivers' subcommand"""
    print("Drivers subcommand!")
    print(args)


def run_command(args: Namespace):
    """Process the CLI for 'run' subcommand"""
    print("Run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    notatoken = ""  # get_token(args)
    driver_instance = driver_from_config(args.driver_config)
    main(driver_instance, args.repo_path, args.dry_run, args.branch_name, notatoken)


def cli(arguments: list[str] | None = None):
    """Run the mass_driver cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    pargs = parse_arguments(arguments)
    pargs.func(pargs)  # Dispatch to the subcommand func (drivers/run)


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
