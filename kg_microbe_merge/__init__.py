"""kg-microbe-merge package."""

from importlib import metadata

from .download import download

try:
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"  # pragma: no cover

__all__ = ["download"]
