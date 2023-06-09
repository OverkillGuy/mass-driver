"""Scan code of repositories"""

import traceback
from copy import deepcopy
from pathlib import Path

from mass_driver.models.activity import ActivityOutcome, IndexedScanResult, ScanResult
from mass_driver.models.repository import IndexedRepos, RepoUrl
from mass_driver.models.scan import ScanLoaded
from mass_driver.repo import clone_if_remote, get_cache_folder


def scan_main(config: ScanLoaded, repos: IndexedRepos, cache: bool) -> ActivityOutcome:
    """Apply the scanners over the repos"""
    repo_count = len(repos)
    cache_folder = get_cache_folder(cache)
    cloned_repos = deepcopy(repos)
    print(f"Processing {repo_count} repos with {len(config.scanners)} scanners")
    scan_results: IndexedScanResult = {}
    for repo_index, (repo_id, repo) in enumerate(repos.items(), start=1):
        print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_id}...")
        scan, repo_local_path = scan_repo(
            config,
            repo.clone_url,
            cache_path=cache_folder,
        )
        scan_results[repo_id] = scan
        cloned_repos[repo_id].cloned_path = repo_local_path
    return ActivityOutcome(
        repos_sourced=cloned_repos,
        scan_result=scan_results,
    )


def scan_repo(
    config: ScanLoaded, repo_url: RepoUrl, cache_path: Path
) -> tuple[ScanResult, Path]:
    """Apply all Scanners on a single repo"""
    scan_result: ScanResult = {}
    repo_gitobj = clone_if_remote(repo_url, cache_path)
    repo_local_path = Path(repo_gitobj.working_dir)
    for scanner in config.scanners:
        try:
            scan_result[scanner.name] = scanner.func(repo_local_path)
        except Exception as e:
            scan_result[scanner.name] = {
                "scan_error": {
                    "exception": str(e),
                    "backtrace": traceback.format_exception(e),
                }
            }
    return scan_result, repo_local_path
