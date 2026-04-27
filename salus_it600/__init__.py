"""Asynchronous Python client for Salus iT600 smart devices."""

from .__version__ import __version__
from .exceptions import (
    IT600AuthenticationError,
    IT600CommandError,
    IT600ConnectionError,
)


def __getattr__(name: str):
    """Load gateway classes lazily so utility imports stay lightweight."""
    if name == "IT600Gateway":
        from .gateway import IT600Gateway

        return IT600Gateway

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
