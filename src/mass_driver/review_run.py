"""Check the status of created PRs, in bulk"""
import logging
from collections import defaultdict

from mass_driver.models.forge import Forge

ERROR_STATUS = "error fetching status"


def review(pr_list: list[str], forge: Forge):
    """Review the status of many given PRs"""
    unique_prs = list(set(pr_list))
    pr_count = len(unique_prs)
    pr_status: dict[str, str] = {}  # Status of each PR from forge
    for pr_index, pr_url in enumerate(unique_prs, start=1):
        try:
            logging.info(f"[{pr_index:03d}/{pr_count:03d}] Fetching PR status...")
            pr_status[pr_url] = forge.get_pr_status(pr_url)
        except Exception as e:
            logging.error(f"Error when fetching PR status {pr_url}. Issue was: {e}")
            pr_status[pr_url] = ERROR_STATUS
            continue
    forge_statuses = forge.pr_statuses
    actual_statuses = set(pr_status.values())
    statuses_not_sorted = actual_statuses - set(forge_statuses) - set([ERROR_STATUS])
    if statuses_not_sorted:
        logging.warning(
            f"Status(es) {statuses_not_sorted} returned by PR not listed by forge, "
            "the ordering of PR statuses below won't be well ordered!",
        )
    count_by_status = {}
    statuses = forge_statuses + list(statuses_not_sorted) + [ERROR_STATUS]
    for forge_status in statuses:
        pr_of_that_status = [
            pr_url for pr_url, pr_state in pr_status.items() if pr_state == forge_status
        ]
        count_by_status[forge_status] = len(pr_of_that_status)
        if not pr_of_that_status:
            continue  # No point listing this status if no PR to show in that state
        logging.info(forge_status.capitalize() + ":")
        for pr_url in sorted(pr_of_that_status):
            logging.info(pr_url)
    logging.info(f"In summary: {len(unique_prs)} unique PRs, of which...")
    for status_name, status_count in count_by_status.items():
        if status_count:
            status_percent = (float(status_count) / pr_count) * 100
            logging.info(f"- {status_count:03} ({status_percent:04.2f}%) {status_name}")
    prlist_by_status = defaultdict(list)
    for pr_url, pr_state in pr_status.items():
        prlist_by_status[pr_state].append(pr_url)
    return prlist_by_status
