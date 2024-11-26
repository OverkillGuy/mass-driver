"""Check the status of created PRs, in bulk"""

import logging
from collections import Counter, defaultdict

from mass_driver.models.forge import Forge

ERROR_STATUS = "error fetching status"


def review(pr_list: list[str], forge: Forge):
    """Review the status of many given PRs"""
    unique_prs = list(set(pr_list))
    pr_count = len(unique_prs)
    status_by_pr: dict[str, str] = {}
    for pr_index, pr_url in enumerate(unique_prs, start=1):
        try:
            logging.info(f"[{pr_index:03d}/{pr_count:03d}] Fetching PR status...")
            status = forge.get_pr_status(pr_url)
            status_by_pr[pr_url] = status
        except Exception as e:
            logging.error(f"Error when fetching PR status {pr_url}. Issue was: {e}")
            status_by_pr[pr_url] = ERROR_STATUS
            continue
    forge_statuses = Counter(status_by_pr.values())
    pr_by_status = defaultdict(list)
    for pr_url, pr_status in status_by_pr.items():
        pr_by_status[pr_status].append(pr_url)
    logging.info(f"In summary: {len(unique_prs)} unique PRs, of which...")
    for status_name, status_count in forge_statuses.most_common():
        if status_count:
            status_percent = (float(status_count) / pr_count) * 100
            logging.info(f"- {status_count:03} ({status_percent:04.2f}%) {status_name}")
    return pr_by_status
