"""Custom exceptions for the bot."""


class ApiIsNotReachable(Exception):
    """Exception for not reaching ISS API."""

    pass


class CoordsNotAwailable(Exception):
    """Exception for not getting ISS coordinates."""

    pass
