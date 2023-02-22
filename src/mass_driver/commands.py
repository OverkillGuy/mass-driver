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
from mass_driver.forge_run import main as forge_main
from mass_driver.migration_run import main as migration_main
from mass_driver.models.activity import ActivityLoaded
from mass_driver.models.migration import load_driver, load_forge, load_migration


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
    """Process the CLI for 'run'"""
    print("Run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    token = get_token()
    activity_str = args.activity_file.read()
    try:
        activity = ActivityLoaded.from_config(activity_str, token)
    except ValueError:
        missing_token_exit()
    if activity.migration is None:
        print("No migration section: skipping migration")
    else:
        migration_result = migration_main(
            activity.migration,
            args.repo_path,
            args.dry_run,
            not args.no_cache,
        )
    print("Migration complete!")
    if activity.forge is None:
        # Nothing else to do, just print completion and exit
        print("No Forge available: end")
        return (migration_result, None)
    # Now guaranteed to have a Forge: pause + forge
    if not args.no_pause:
        print("Review the commits now.")
        pause_until_ok("Type y/yes/continue to run the Forge")
    forge_result = forge_main(activity.forge, args.repo_path)
    return (migration_result, forge_result)


def run_migration_command(args: Namespace):
    """Process the CLI for 'run-migration' subcommand"""
    print("Migration-run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    migration_config_str = args.migration_file.read()
    migration_file = load_migration(migration_config_str)
    migration = load_driver(migration_file)
    return migration_main(
        migration,
        args.repo_path,
        args.dry_run,
        not args.no_cache,
    )


def run_forge_command(args: Namespace):
    """Process the CLI for 'run-forge' subcommand"""
    print("Forge-run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    token = get_token()
    if token is None:
        return missing_token_exit()
    forge_config_str = args.forge_file.read()
    forge = load_forge(forge_config_str, token)
    return forge_main(forge, args.repo_path)


def get_token() -> str | None:
    """Grab the Forge API Token if any"""
    return os.getenv("FORGE_TOKEN")


def missing_token_exit():
    """Exit in case of bad token"""
    print(
        "Missing API token: set FORGE_TOKEN envvar",
        file=sys.stderr,
    )
    exit(2)  # Simulate the argparse behaviour of exiting on bad args


def pause_until_ok(message: str):
    """Halt until keyboard input is a variant of YES"""
    continue_asking = True
    while continue_asking:
        typed_text = input(message)
        if typed_text.lower() in ["y", "yes", "ok", "c", "continue"]:
            continue_asking = False
