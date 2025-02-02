"""The status of a single Repo's processing"""

from enum import Enum
from traceback import format_exception

from pydantic import BaseModel

ScanResult = dict[str, dict]
"""The output of one or more scanner(s) on a single repo, indexed by scanner-name"""


class Phase(str, Enum):
    """The "Phase" a single Repository is going through"""

    SOURCE = "SOURCE"
    CLONE = "CLONE"
    SCAN = "SCAN"
    PATCH = "PATCH"
    FORGE = "FORGE"


class ExceptionRecord(BaseModel):
    """A serialized version of an Exception"""

    exception_type: str
    """The type of exception thrown"""
    exception_details: str
    """The string version of the exception"""
    backtrace: list[str]
    """The exception backtrace as array of string"""

    @classmethod
    def from_exception(cls, e: Exception):
        """Create an ExceptionRecord object from Exception object"""
        return cls(
            exception_type=e.__class__.__name__,
            exception_details=str(e),
            backtrace=format_exception(e),
        )


class Error(BaseModel):
    """Captures an issue during a specific phase"""

    activity: Phase
    """During which activity did the error occur"""
    # context: str
    # """A short string explaining what was attempted, that failed"""
    error: ExceptionRecord
    """The record of the exception, what went wrong"""

    @classmethod
    def from_exception(cls, activity: Phase, exception: Exception):
        """Create an Error from Exception object"""
        return cls(activity=activity, error=ExceptionRecord.from_exception(exception))
