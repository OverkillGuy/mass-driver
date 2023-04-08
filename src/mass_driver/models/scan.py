"""Scanners for repos"""
from pathlib import Path
from typing import Any, Callable, NamedTuple

ScannerFunc = Callable[[Path], dict[str, Any]]
"""The scanner function itself, taking cloned repo, returning a dict of findings"""


class Scanner(NamedTuple):
    """A single scanner"""

    name: str
    """The scanner's name (plugin name)"""
    func: ScannerFunc
    """The scanner function itself"""
