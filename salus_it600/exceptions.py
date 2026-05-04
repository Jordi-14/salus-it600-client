"""Exceptions for Salus iT600 smart devices."""


class IT600Error(Exception):
    """Salus iT600 exception."""


class IT600AuthenticationError(IT600Error):
    """Salus iT600 authentication exception."""


class IT600CommandError(IT600Error):
    """Salus iT600 command exception."""


class IT600ConnectionError(IT600Error):
    """Salus iT600 connection exception."""


class IT600UnsupportedFirmwareError(IT600Error):
    """Salus gateway firmware uses an unsupported protocol."""
