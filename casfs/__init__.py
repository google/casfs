"""Docs on CASFS.
"""

from casfs.base import CASFS
from casfs.util import HashAddress

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ("CASFS", "HashAddress")
