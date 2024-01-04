"""
RadTraQ
=======
"""
from . import plotting, proc, tests, utils  # noqa
import importlib.metadata as _importlib_metadata

# Get the version
try:
    __version__ = _importlib_metadata.version('radtraq')
except _importlib_metadata.PackageNotFoundError:
    # package is not installed
    __version__ = '0.0.0'
