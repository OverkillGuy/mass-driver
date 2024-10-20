"""A few basic scanners to get people started"""

from pathlib import Path
from typing import Any


def has_dir(repo: Path, target: str) -> bool:
    """Check target directory exists under repo"""
    return (repo / Path(target)).is_dir()


def has_file(repo: Path, target: str) -> bool:
    """Check file dir_to_check exists under repo"""
    return (repo / Path(target)).is_file()


def rootlevel_files(repo: Path) -> dict[str, Any]:
    """Detect some files at the root of the repo"""
    return {
        "changelog_md": has_file(repo, "CHANGELOG.md"),
        "readme_md": has_file(repo, "README.md"),
        "license": has_file(repo, "LICENSE"),
        "makefile": has_file(repo, "Makefile"),
        "gitignore": has_file(repo, ".gitignore"),
        "dockerfile": has_file(repo, "Dockerfile"),
    }


def dockerfile_from_scanner(repo: Path) -> dict[str, Any]:
    """Report the repo's Dockerfile's FROM line(s)"""
    dockerfile_path = repo / "Dockerfile"
    dockerfile_exists = dockerfile_path.is_file()
    if not dockerfile_exists:
        return {"dockerfile_exists": False, "dockerfile_from": None}
    dkr_lines = dockerfile_path.read_text().splitlines()
    dkr_from_lines = [line for line in dkr_lines if line.startswith("FROM")]
    return {"dockerfile_exists": True, "dockerfile_from_lines": dkr_from_lines}
