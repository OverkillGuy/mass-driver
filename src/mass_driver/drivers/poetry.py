"""Poetry package version bump"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from jsonpointer import resolve_pointer, set_pointer
    from poetry.core.pyproject.toml import PyProjectTOML

    # We want to hard fail only when actively USING the dependencies, not just importing
    # it at toplevel (not actively using) ==> Set a flag for availability of deps,
    # to check at runtime and raise only then
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

    pass  # Shouldn't error at import time (docs, CLI), but instead at runtime

from mass_driver.model import PatchDriver


def get_pyproject(repo_path: Path):
    """Grab the pyproject object"""
    return PyProjectTOML(repo_path / "pyproject.toml")


@dataclass
class Poetry(PatchDriver):
    """Bump a package's major version in the pyproject.toml

    Using the following:

    .. code:: python

        Poetry(package="pytest",target_major="8",package_group="test")

    Will provide the following diff:

    .. code-block:: diff

        [tool.poetry.group.test.dependencies]
        -pytest = "7.*"
        +pytest = "8.*"
    """

    package: str
    """The target package to update major version for"""
    target_major: str
    """Major version to which to upgrade the package if possible"""
    package_group: Optional[str] = None
    """Package group if any(as defined in poetry>1.2) where to find package"""

    @property
    def json_pointer(self):
        """Get the JSON Pointer (RFC6901) for the package we're looking for"""
        if self.package_group:
            return (
                f"/tool/poetry/group/{self.package_group}/dependencies/{self.package}"
            )
        else:
            return f"/tool/poetry/dependencies/{self.package}"

    def run(self, repo: Path, dry_run: bool = True) -> bool:
        """Process the major bump file"""
        if not DEPS_AVAILABLE:
            raise ImportError(
                "Missing dependencies required for this Driver. "
                "Please install the package fully"
            )
        project = get_pyproject(repo)
        dep_version = resolve_pointer(project.data, self.json_pointer, None)
        if not dep_version:
            print(f"Didn't find {self.package} in pyproject.toml test deps!")
            return False
        major_version, *other_versions = dep_version.split(".")
        inferior_version = int(major_version) < int(self.target_major)
        if inferior_version and not dry_run:
            set_pointer(project.data, self.json_pointer, f"{self.target_major}.*")
            project.save()
        return inferior_version
