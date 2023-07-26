"""The different main commands of the mass-driver tool"""

import logging
from argparse import Namespace
from typing import Callable, Optional

from pydantic import ValidationError

from mass_driver.activity_run import run
from mass_driver.discovery import (
    discover_drivers,
    discover_forges,
    discover_sources,
    get_driver_entrypoint,
    get_forge,
    get_forge_entrypoint,
    get_scanners,
    get_source_entrypoint,
)
from mass_driver.forge_run import main as forge_main
from mass_driver.forge_run import pause_until_ok
from mass_driver.models.activity import ActivityLoaded, ActivityOutcome
from mass_driver.models.repository import IndexedRepos, Repo
from mass_driver.review_run import review


def drivers_command(args: Namespace):
    """Process the CLI for 'Drivers' subcommand"""
    return plugins_command(args, "driver", get_driver_entrypoint, discover_drivers)


def forges_command(args: Namespace):
    """Process the CLI for 'Forges' subcommand"""
    return plugins_command(args, "forge", get_forge_entrypoint, discover_forges)


def sources_command(args: Namespace):
    """Process the CLI for 'Sources' subcommand"""
    return plugins_command(args, "source", get_source_entrypoint, discover_sources)


def plugins_command(
    args: Namespace, plugin: str, entrypoint: Callable, discover: Callable
):
    """Process the CLI for a generic plugin subcommand"""
    if args.info:
        target_plugin = args.info
        try:
            plugin_obj = entrypoint(target_plugin)
            logging.info(
                f"Plugin name: {plugin_obj.name}; Import path: "
                f"{plugin_obj.module}; Class: {plugin_obj.attr}"
            )
            logging.info(plugin_obj.load().__doc__)
            return
        except ImportError as e:
            logging.error("Error importing plugin", exc_info=e)
            logging.error(f"Try `mass driver {plugin}s --list`")
            return
    # if args.list:  # Implicit
    plugins = discover()
    logging.info(f"Available {plugin}s:")
    for plugin_obj in plugins:
        logging.info(plugin_obj.name)
    return True


def run_command(args: Namespace) -> ActivityOutcome:
    """Process the CLI for 'run'"""
    logging.info("Run mode!")
    activity_str = args.activity_file.read()
    try:
        activity = ActivityLoaded.from_config(activity_str)
    except ValidationError as e:
        config_error_exit(e)
    # Source discovery to know what repos to patch/forge/scan
    source_config = activity.source
    repos_sourced = source_repolist_args(args)
    if repos_sourced is None:  # No repo-list from CLI flags: call Source
        repos_sourced = source_config.source.discover()
    if needs_run(activity):
        run_result = run(
            activity,
            repos_sourced,
            not args.no_cache,
        )
    else:
        logging.info("No clone needed: skipping")
        run_result = ActivityOutcome(repos_sourced=repos_sourced)
    logging.info("Main phase complete!")
    if activity.forge is None:
        # Nothing else to do, just print completion and exit
        logging.info("No Forge: end")
        maybe_save_outcome(args, run_result)
        return run_result
    # Now guaranteed to have a Forge: pause + forge
    if not args.no_pause:
        logging.info("Review the commits now.")
        pause_until_ok("Type y/yes/continue to run the Forge\n")
    forge_result = forge_main(activity.forge, run_result)
    maybe_save_outcome(args, forge_result)
    return forge_result


def scanners_command(args: Namespace):
    """Process the CLI for 'scan'"""
    logging.info("Available scanners:")
    scanners = get_scanners()
    for scanner in scanners:
        logging.info(scanner.name)
    return True


def review_pr_command(args: Namespace):
    """Review a list of Pull Requests"""
    logging.info("Pull request review mode!")
    forge_class = get_forge(args.forge)
    forge = forge_class()  # Credentials via env
    pr_list = args.pr
    if args.pr_filelist:
        pr_list = args.pr_filelist.read().strip().split("\n")
    review(pr_list, forge)
    return 0


def config_error_exit(e: ValidationError):
    """Exit in case of bad config models"""
    model_class = e.model.__base__
    try:
        # Assume the class failing validation has env prefix
        env_prefix = model_class.Config.env_prefix
    except Exception:
        logging.error("Missing config", exc_info=e)
        raise
    # We have a valid env_prefix now, use it to show missing envvar
    model_class_name = model_class.__name__
    for error in e.errors():
        if error["type"] == "value_error.missing":
            envvars = [env_prefix + var.upper() for var in error["loc"]]
            logging.error(
                f"Missing {model_class_name} config: Set envvar(s) {', '.join(envvars)}"
            )
        else:
            logging.error(f"{model_class_name} config validation error: {error}")
    raise e  # exit code = Simulate the argparse behaviour of exiting on bad args


def source_repolist_args(args) -> Optional[IndexedRepos]:
    """Read the repo from args, if any"""
    repos = read_repolist(args)
    if repos is not None:
        return (
            {url: Repo(repo_id=url, clone_url=url) for url in repos} if repos else None
        )
    return None


def read_repolist(args) -> Optional[list[str]]:
    """Read the repo-list or repo-path arg, if any"""
    if args.repo_path:
        return args.repo_path
    if args.repo_filelist:
        return args.repo_filelist.read().strip().split("\n")
    return None


def maybe_save_outcome(args: Namespace, outcome: ActivityOutcome):
    """Consider saving the outcome"""
    if not args.json_outfile:
        return
    save_outcome(outcome, args.json_outfile)
    logging.info("Saved outcome to given JSON file")


def save_outcome(outcome: ActivityOutcome, out_file):
    """Save the output to given JSON file handle"""
    out_file.write(outcome.json(indent=2))
    out_file.write("\n")


def needs_run(activity: ActivityLoaded) -> bool:
    """Check if we need to call the activity_run command = Clone/Mig/Scan step

    We usually do if: migration OR scan OR forge with git_push_first=True

    Last one because git_push requires resolving ssh clone url to local repo path
    which is what clone step does in activity_run
    """
    got_mig = activity.migration is not None
    got_scan = activity.scan is not None
    got_forge_clone = activity.forge is not None and activity.forge.git_push_first
    # activity-running is only needed if we need some clone:
    return got_mig or got_scan or got_forge_clone
