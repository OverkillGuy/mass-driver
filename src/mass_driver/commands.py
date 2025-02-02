"""The different main commands of the mass-driver tool"""

import logging
import sys
from argparse import Namespace
from typing import Callable, Optional

from pydantic import ValidationError
from tomllib import TOMLDecodeError

from mass_driver.activity_run import sequential_run, thread_run
from mass_driver.discovery import (
    discover_drivers,
    discover_forges,
    discover_scanners,
    discover_sources,
    get_driver_entrypoint,
    get_forge,
    get_forge_entrypoint,
    get_source_entrypoint,
)
from mass_driver.errors import ActivityLoadingException
from mass_driver.forge_run import main as forge_main
from mass_driver.forge_run import pause_until_ok
from mass_driver.models.activity import (
    ActivityLoaded,
    ActivityOutcome,
    bad_activity_error,
)
from mass_driver.models.outcome import RepoOutcome
from mass_driver.models.repository import IndexedRepos, SourcedRepo
from mass_driver.models.status import Phase
from mass_driver.review_run import review
from mass_driver.summarize import summarize_forge, summarize_migration, summarize_source


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
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger("run")
    logger.info("Run mode!")
    if args.debug:
        breakpoint()
    activity_str = args.activity_file.read()
    try:
        activity = ActivityLoaded.from_config(activity_str)
    except ActivityLoadingException as e:
        errors = e.args[0]
        for error in errors:
            logger.error(error)
        raise e
    except TOMLDecodeError as e:
        logger.error("Error reading the given mass-driver activity file")
        logger.exception(e)
        raise e
    except (ValidationError, ImportError, Exception) as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.error("Unknown exception thrown during mass-driver activity file read")
        logger.exception(e)
        raise e
    # Source discovery to know what repos to patch/forge/scan
    sum_logger = logging.getLogger("summarize")
    out = maybe_discover_sources(args, activity.source, sum_logger)
    if needs_run(activity):
        run_variant = thread_run if args.parallel else sequential_run
        run_result = run_variant(
            activity,
            out,
            not args.no_cache,
        )
        if activity.migration is not None:
            summarize_migration(run_result, sum_logger)
    else:
        logger.info("No clone needed: skipping")
        run_result = out
    logger.info("Main phase complete!")
    if activity.forge is None:
        # Nothing else to do, just print completion and exit
        logger.info("No Forge: end")
        maybe_save_outcome(args, run_result)
        return run_result
    # Now guaranteed to have a Forge: pause + forge
    if not args.no_pause:
        logger.info("Review the commits now.")
        pause_until_ok("Type y/yes/continue to run the Forge\n")
    result = forge_main(activity.forge, run_result)
    maybe_save_outcome(args, result)
    summarize_forge(result, sum_logger)
    return result


def scanners_command(args: Namespace):
    """Process the CLI for 'scan'"""
    logging.info("Available scanners:")
    scanners = discover_scanners()
    for scanner in scanners:
        logging.info(scanner.name)
    return True


def review_pr_command(args: Namespace):
    """Review a list of Pull Requests"""
    logging.info("Pull request review mode!")
    try:
        forge_class = get_forge(args.forge)
        forge = forge_class()  # Credentials via env
    except ValidationError as e:
        errors = bad_activity_error(e, "Forge")
        for error in errors:
            logging.error(error)
        return 1
    pr_list = args.pr
    if args.pr_filelist:
        pr_list = args.pr_filelist.read().strip().split("\n")
    review(pr_list, forge)
    return 0


def source_repolist_args(args) -> Optional[ActivityOutcome]:
    """Read the repo from args, if any"""
    repos = read_repolist(args)
    if repos is None:
        return None
    repo_dict = {
        url: RepoOutcome(
            repo_id=url,
            status=Phase.SOURCE,
            source=SourcedRepo(repo_id=url, clone_url=url),
        )
        for url in repos
    }
    return ActivityOutcome(repos=repo_dict)


def read_repolist(args) -> Optional[list[str]]:
    """Read the repo-list or repo-path arg, if any"""
    if args.repo_path:
        return args.repo_path
    if args.repo_filelist:
        return args.repo_filelist.read().strip().split("\n")
    return None


def maybe_save_outcome(args: Namespace, outcome: ActivityOutcome):
    """Consider saving the outcome"""
    if not args.output:
        return
    save_outcome(outcome, args.output)
    logging.info("Saved outcome to given JSON file")


def save_outcome(outcome: ActivityOutcome, out_file):
    """Save the output to given JSON file handle"""
    out_file.write(outcome.model_dump_json(indent=2))
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


def sourced_to_outcome(r: IndexedRepos) -> ActivityOutcome:
    """Convert the result of sourcing back to a full activity"""
    repos = {}
    for repo_id, sourced_repo in r.items():
        repos[repo_id] = RepoOutcome(
            repo_id=repo_id, status=Phase.SOURCE, source=sourced_repo
        )
    return ActivityOutcome(repos=repos)


def maybe_discover_sources(args, source_config, sum_logger) -> ActivityOutcome:
    """Discover sources, either CLI or properly"""
    repos_sourced = source_repolist_args(args)
    if repos_sourced is None:  # No repo-list from CLI flags: call Source
        repos_sourced = source_config.source.discover()
        out = sourced_to_outcome(repos_sourced)
    else:
        out = repos_sourced
    summarize_source(out, sum_logger)
    return out
