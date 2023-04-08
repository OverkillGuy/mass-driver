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


def rootlevel_folders(repo: Path) -> dict[str, Any]:
    """Detect some folders at the root of the repo"""
    return {
        "src": has_dir(repo, "src/"),
        "tests": has_dir(repo, "tests/"),
        "docs": has_dir(repo, "docs/"),
    }
