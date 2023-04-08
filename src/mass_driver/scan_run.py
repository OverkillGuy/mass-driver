"""Scan code of repositories"""

import traceback
from pathlib import Path

from mass_driver.models.activity import (
    ActivityOutcome,
    IndexedScanResult,
    RepoPathLookup,
    RepoUrl,
    ScanResult,
)
from mass_driver.models.scan import ScanLoaded
from mass_driver.repo import clone_if_remote, get_cache_folder


def scan_main(
    config: ScanLoaded, repo_urls: list[RepoUrl], cache: bool
) -> ActivityOutcome:
    """Apply the scanners over the repos"""
    repo_count = len(repo_urls)
    cache_folder = get_cache_folder(cache)
    print(f"Processing {repo_count} repos with {len(config.scanners)} scanners")
    scan_results: IndexedScanResult = {}
    repo_local_paths: RepoPathLookup = {}
    for repo_index, repo_url in enumerate(repo_urls, start=1):
        print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_url}...")
        scan, repo_local_path = scan_repo(
            config,
            repo_url,
            cache_path=cache_folder,
        )
        scan_results[repo_url] = scan
        repo_local_paths[repo_url] = repo_local_path
    return ActivityOutcome(
        repos_input=repo_urls,
        local_repos_path=repo_local_paths,
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
