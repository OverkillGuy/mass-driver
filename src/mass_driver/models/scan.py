"""Scanners for repos"""
from pathlib import Path
from typing import Any, Callable, NamedTuple

from pydantic import BaseModel

ScannerFunc = Callable[[Path], dict[str, Any]]
"""The scanner function itself, taking cloned repo, returning a dict of findings"""


class Scanner(NamedTuple):
    """A single scanner"""

    name: str
    """The scanner's name (plugin name)"""
    func: ScannerFunc
    """The scanner function itself"""


class ScanFile(BaseModel):
    """Config file for Scan Activity"""

    scanner_names: list[str]
    """The list of scanner plugins to use"""


class ScanLoaded(ScanFile):
    """The post-loaded version of ScanFile"""

    scanners: list[Scanner]
    """Loaded Scanner objects"""
