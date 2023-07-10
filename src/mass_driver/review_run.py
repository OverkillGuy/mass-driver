"""Check the status of created PRs, in bulk"""
import sys
from collections import defaultdict
from typing import Any

from mass_driver.discovery import get_forge
from mass_driver.forges.github import detect_pr_info

# TODO: Expand this for more than one Forge (Forge-specific PR status)


def review(pr_list: list[str]):
    """Review the status of many given PRs"""
    pr_details: dict[str, dict] = defaultdict(dict)
    pr_infos: dict[str, tuple[str, str]] = {}
    unique_prs = list(set(pr_list))
    # Separate URLs into repo + PR ID
    for pr_url in unique_prs:
        try:
            owner, repo, prnum = detect_pr_info(pr_url)
            owner_repo_prnum = (f"{owner}/{repo}", prnum)
            pr_infos[pr_url] = owner_repo_prnum
        except ValueError:
            print(
                f"Invalid PR URL: {pr_url}",
                file=sys.stderr,
            )
            continue
    # Create a Forge object = auth to github
    github_forge_class = get_forge("github")
    forge = github_forge_class()  # Credentials via env
    pr_objs: dict[str, Any] = {}
    for pr_url, pr_info in pr_infos.items():
        try:
            repo, pr_id = pr_info
            pr_obj = forge.get_pr(repo, pr_id)
            pr_objs[pr_url] = pr_obj
        except Exception as e:
            print(
                f"Issue when fetching PR info for {repo=}, {pr_id=}. Issue was: {e}",
                file=sys.stderr,
            )
            continue
    for pr_url, pr in pr_objs.items():
        pr_details[pr_url]["merged"] = pr.merged
        pr_details[pr_url]["state"] = pr.state
        pr_details[pr_url]["mergeable"] = pr.mergeable
        pr_details[pr_url]["draft"] = pr.draft
        # pr_details["statuses_head"] = pr.get_commits()[pr.commits-1]. if pr_detail["merged"]

    merged = sorted(
        [pr_url for pr_url, pr_detail in pr_details.items() if pr_detail["merged"]]
    )
    count_merged = len(merged)
    closed = sorted(
        [
            pr_url
            for pr_url, pr_detail in pr_details.items()
            if pr_detail["state"] == "closed"
        ]
    )
    closed_not_merged = sorted(list(set(closed) - set(merged)))
    count_closed = len(closed_not_merged)
    mergeable = sorted(
        [pr_url for pr_url, pr_detail in pr_details.items() if pr_detail["mergeable"]]
    )
    count_mergeable = len(mergeable)
    non_mergeable = sorted(list(set(pr_objs.keys()) - set(closed) - set(mergeable)))
    count_non_mergeable = len(non_mergeable)

    print()
    print("Merged:")
    if not merged:
        print("None!")
    for pr_url in merged:
        print(pr_url)
    print()
    print("Closed (but not merged):")
    if not closed_not_merged:
        print("None!")
    for pr_url in closed_not_merged:
        print(pr_url)
    print()
    print("Mergeable (no conflict):")
    if not mergeable:
        print("None!")
    for pr_url in mergeable:
        print(pr_url)
    print()
    print("Non-mergeable (conflicts):")
    if not non_mergeable:
        print("None!")
    for pr_url in non_mergeable:
        print(pr_url)
    print()
    print(
        f"Received {len(pr_list)} URLs, "
        f"{len(pr_infos)} valid PR URLs, "
        f"{len(pr_objs)} actual PRs"
    )
    print(
        f"Of which: {count_merged} merged, "
        f"{count_closed} closed, "
        f"{count_mergeable} mergeable, "
        f"{count_non_mergeable} have conflicts"
    )
    # TODO Explore more of the PR states to make this response more useful
