"""Different types of errors of Mass-driver"""


class MassDriverException(Exception):
    """The base for all exceptions mass-driver uses"""

    pass


class ActivityLoadingException(MassDriverException):
    """Failed to load the full activity"""

    pass
