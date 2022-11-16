"""A JSON Patch (RFC6902) PatchDriver"""


import json
from pathlib import Path
from typing import Any

try:
    from jsonpatch import JsonPatch as Patch

    # We want to hard fail only when actively USING the dependencies, not just importing
    # it at toplevel (not actively using) ==> Set a flag for availability of deps,
    # to check at runtime and raise only then
    DEPS_AVAILABLE = True
except ImportError:
    Patch = None  # Define a dummy type to avoid crash
    DEPS_AVAILABLE = False


from mass_driver.model import PatchDriver


class JsonPatch(PatchDriver):
    """Apply a JSON patch (RFC6902) on given file"""

    target_file: Path
    """File on which to apply Json Patch"""
    patch: Patch
    """JSON Patch object, from RFC 6902"""

    def __init__(self, target_file: Path, path: str, op: str, value: Any):
        """
        RFC6902 JSON patch application in target file

        target_file: The JSON file on which to apply a mutation
        path: RFC6902 'path', to know where to apply operation
        op: RFC6902 'op', operation
        value: RFC6902 'value', to apply at path

        """
        self.target_file = target_file
        single_patch = dict(op=op, path=path, value=value)
        self.patch = Patch([single_patch])

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Patch the given file"""
        if not DEPS_AVAILABLE:
            raise ImportError(
                "Missing dependencies required for this Driver. "
                "Please install the package fully"
            )
        json_filepath_abs = repo / self.target_file
        if not json_filepath_abs.is_file():
            raise RuntimeError("File not found: can't patch!")
        with open(json_filepath_abs) as json_file:
            json_dict = json.load(json_file)
        patched_json = self.patch.apply(json_dict)
        if dry_run:
            return True  # Skip the saving of the dict = no file changes persist
        breakpoint()
        with open(json_filepath_abs, "w") as json_outfile:
            # TODO: Consider pretty-print indentation param
            json.dump(patched_json, json_outfile)
        return True
