"""Docs on CASFS.
"""

from casfs.casfs import CASFS
from casfs.util import HashAddress

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ("CASFS", "HashAddress")
