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


class IT600ValidationError(IT600Error, ValueError):
    """A command argument is not valid for the target device.

    Subclasses ValueError so existing ``except ValueError`` handlers keep working.
    """


class IT600DeviceNotFoundError(IT600Error, KeyError):
    """The requested device is not in the gateway cache.

    Subclasses KeyError so existing ``except KeyError`` handlers keep working.
    """
