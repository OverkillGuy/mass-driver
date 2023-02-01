"""The different main commands of the mass-driver tool"""

import os
import sys
from argparse import Namespace

from mass_driver.discovery import (
    discover_drivers,
    discover_forges,
    get_driver_entrypoint,
    get_forge_entrypoint,
)
from mass_driver.main import main
from mass_driver.migration import load_migration


def drivers_command(args: Namespace):
    """Process the CLI for 'Drivers' subcommand"""
    if args.info:
        target_driver = args.info
        try:
            driver = get_driver_entrypoint(target_driver)
            print(
                f"Plugin name: {driver.name}; Import path: {driver.module}; Class: {driver.attr}"
            )
            print(driver.load().__doc__)
            return
        except ImportError as e:
            print(str(e), file=sys.stderr)
            print("Try `mass driver drivers --list`", file=sys.stderr)
            return
    # if args.list:  # Implicit
    drivers = discover_drivers()
    print("Available drivers:")
    for driver in drivers:
        print(f"{driver.name}")
    return


def forges_command(args: Namespace):
    """Process the CLI for 'Forges' subcommand"""
    if args.info:
        target_forge = args.info
        try:
            forge = get_forge_entrypoint(target_forge)
            print(
                f"Plugin name: {forge.name}; Import path: {forge.module}; Class: {forge.attr}"
            )
            print(forge.load().__doc__)
            return
        except ImportError as e:
            print(str(e), file=sys.stderr)
            print("Try `mass driver forges --list`", file=sys.stderr)
            return
    # if args.list:  # Implicit
    forges = discover_forges()
    print("Available forges:")
    for forge in forges:
        print(f"{forge.name}")
    return


def run_command(args: Namespace):
    """Process the CLI for 'run' subcommand"""
    print("Run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    notatoken = ""  # get_token(args)
    migration_config_str = args.migration_file.read()
    migration = load_migration(migration_config_str)
    return main(
        migration,
        args.repo_path,
        args.dry_run,
        notatoken,
        not args.no_cache,
    )


def get_token(args: Namespace) -> str:
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
