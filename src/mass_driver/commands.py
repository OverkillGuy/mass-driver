"""The different main commands of the mass-driver tool"""

import sys
from argparse import Namespace
from pathlib import Path

from pydantic import ValidationError

from mass_driver.discovery import (
    discover_drivers,
    discover_forges,
    get_driver_entrypoint,
    get_forge_entrypoint,
)
from mass_driver.forge_run import main as forge_main
from mass_driver.forge_run import pause_until_ok
from mass_driver.migration_run import main as migration_main
from mass_driver.models.activity import ActivityLoaded, ActivityOutcome


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


def run_command(args: Namespace) -> ActivityOutcome:
    """Process the CLI for 'run'"""
    print("Run mode!")
    if args.repo_filelist:
        args.repo_path = args.repo_filelist.read().strip().split("\n")
    activity_str = args.activity_file.read()
    try:
        activity = ActivityLoaded.from_config(activity_str)
    except ValidationError as e:
        forge_config_error_exit(e)
    if activity.migration is None:
        print("No migration section: skipping migration")
        migration_result = ActivityOutcome(
            repos_input=args.repo_path,
            local_repos_path={r: Path(r) for r in args.repo_path},
        )
    else:
        migration_result = migration_main(
            activity.migration,
            args.repo_path,
            not args.no_cache,
        )
    print("Migration complete!")
    if activity.forge is None:
        # Nothing else to do, just print completion and exit
        print("No Forge available: end")
        return migration_result
    # Now guaranteed to have a Forge: pause + forge
    if not args.no_pause:
        print("Review the commits now.")
        pause_until_ok("Type y/yes/continue to run the Forge\n")
    forge_result = forge_main(activity.forge, migration_result)
    return forge_result


def forge_config_error_exit(e: ValidationError):
    """Exit in case of bad forge config"""
    for error in e.errors():
        if error["type"] == "value_error.missing":
            envvars = ["FORGE_" + var.upper() for var in error["loc"]]
            print(
                f"Missing Forge config: Set envvar(s) {', '.join(envvars)}",
                file=sys.stderr,
            )
        else:
            print(
                f"Forge config validation error: {error}",
                file=sys.stderr,
            )
    raise e  # exit code = Simulate the argparse behaviour of exiting on bad args
