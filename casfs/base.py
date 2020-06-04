#!/usr/bin/python
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for CASFS class.

Potential next steps:

TODO - store the actual FULL hash at the end of each.

TODO - we need a function that will provide a temp path... and when we leave
the context manager, move the stuff from the temp path into the content
addressable store.

"""

import hashlib
import io
import os
from contextlib import closing
from typing import Iterable, Optional, Text, Tuple, Union

import fs as pyfs
from fs.permissions import Permissions

import casfs.util as u

Key = Union[str, u.HashAddress]


class CASFS(object):
  """Content addressable file manager. This is the Blueshift rewrite of
  https://github.com/dgilland/hashfs, using
  https://github.com/PyFilesystem/pyfilesystem2.

    Attributes:
        root: Either an instance of pyfs.base.FS, or a URI string parseable by
            pyfilesystem.
        depth: Depth of subfolders to create when saving a file. Defaults to 2,
            which means that actual hashes will be nested two items deep.
        width: Width of each subfolder to create when saving a file. This means
            that blocks of `width` characters of the hash will be used to
            bucket content into each successive folder.
        algorithm: Hash algorithm to use when computing file hash. Algorithm
            should be available in `hashlib` module, ie, a member of
            `hashlib.algorithms_available`. Defaults to `'sha256'`.
        dmode: Directory mode permission to set for subdirectories. Defaults to
            `0o755` which allows owner/group to read/write and everyone else to
            read and everyone to execute.

  """

  def __init__(self,
               root: Union[pyfs.base.FS, str],
               depth: Optional[int] = 2,
               width: Optional[int] = 2,
               algorithm: hashlib.algorithms_available = "sha256",
               dmode: Optional[int] = 0o755):

    self.fs = u.load_fs(root)
    self.depth = depth
    self.width = width
    self.algorithm = algorithm
    self.dmode = dmode

  def put(self, content) -> u.HashAddress:
    """Store contents of `content` in the backing filesystem using its content hash
    for the address.

    Args:
      content: Readable object or path to file.

    Returns:
      File's hash address.

    """
    with closing(u.Stream(content, fs=self.fs)) as stream:
      hashid = self._computehash(stream)
      path, is_duplicate = self._copy(stream, hashid)

    return u.HashAddress(hashid, path, is_duplicate)

  def get(self, k: Key) -> Optional[u.HashAddress]:
    """Return :class:`HashAddress` from given id or path. If `k` does not refer to
       a valid file, then `None` is returned.

    Args:
      k: Address ID or path of file.

    Returns:
      File's hash address or None.

    """
    path = self._fs_path(k)

    if path is None:
      return None

    return u.HashAddress(self._unshard(path), path)

  def open(self, k: Key) -> io.IOBase:
    """Return open IOBase object from given id or path.

        Args:
            k: Address ID or path of file.

        Returns:
            Buffer: A read-only `io` buffer into the underlying filesystem.

        Raises:
            IOError: If file doesn't exist.

    """
    path = self._fs_path(k)
    if path is None:
      raise IOError("Could not locate file: {0}".format(k))

    return self.fs.open(path, mode='rb')

  def delete(self, k: Key) -> None:
    """Delete file using id or path. Remove any empty directories after
        deleting. No exception is raised if file doesn't exist.

        Args:
            k: Key of the file to delete..
        """
    path = self._fs_path(k)
    if path is None:
      return None

    try:
      self.fs.remove(path)
    except OSError:  # pragma: no cover
      # Attempting to delete a directory.
      pass
    else:
      print("REMOVING", pyfs.path.dirname(path))
      self._remove_empty(pyfs.path.dirname(path))

  def files(self) -> Iterable[Text]:
    """Return generator that yields all files in the :attr:`fs`.

    """
    return (pyfs.path.relpath(p) for p in self.fs.walk.files())

  def folders(self) -> Iterable[Text]:
    """Return generator that yields all directories in the :attr:`fs` that contain
        files.

    """
    for step in self.fs.walk():
      if step.files:
        yield step.path

  def count(self) -> int:
    """Return count of the number of files in the backing :attr:`fs`.
        """
    return sum(1 for _, info in self.fs.walk.info() if info.is_file)

  def size(self) -> int:
    """Return the total size in bytes of all files in the :attr:`root`
        directory.
        """
    return sum(info.size
               for _, info in self.fs.walk.info(namespaces=['details'])
               if info.is_file)

  def exists(self, k: Key) -> bool:
    """Check whether a given file id or path exists on disk."""
    return bool(self._fs_path(k))

  def repair(self) -> Iterable[Text]:
    """Repair any file locations whose content address doesn't match its file path.
    Returns a sequence of repaired files.

    """
    repaired = []
    corrupted = self._corrupted()

    for path, address in corrupted:
      if self.fs.isfile(address.relpath):
        # File already exists so just delete corrupted path.
        self.fs.remove(path)

      else:
        # File doesn't exist, so move it.
        self._makedirs(pyfs.path.dirname(address.relpath))
        self.fs.move(path, address.relpath)

      repaired.append((path, address))

    # check for empty directories created by the repair.
    for d in {pyfs.path.dirname(p) for p, _ in repaired}:
      self._remove_empty(d)

    return repaired

  def __contains__(self, k: Key) -> bool:
    """Return whether a given file id or path is contained in the
        :attr:`root` directory.
        """
    return self.exists(k)

  def __iter__(self) -> Iterable[str]:
    """Iterate over all files in the backing store."""
    return self.files()

  def __len__(self) -> int:
    """Return count of the number of files tracked by the backing filesystem.

    """
    return self.count()

  def _computehash(self, stream: u.Stream) -> str:
    """Compute hash of file using :attr:`algorithm`."""
    return u.computehash(stream, self.algorithm)

  def _copy(self, stream: u.Stream, hashid: str) -> Tuple[Text, bool]:
    """Copy the contents of `stream` onto disk.

        Returns a pair of

        - relative path,
        - boolean noting whether or not we have a duplicate.

        """
    path = self._hashid_to_path(hashid)

    if self.fs.isfile(path):
      is_duplicate = True

    else:
      # Only move file if it doesn't already exist.
      is_duplicate = False
      self._makedirs(pyfs.path.dirname(path))
      with closing(self.fs.open(path, mode='wb')) as p:
        for data in stream:
          p.write(u.to_bytes(data))

    return (path, is_duplicate)

  def _remove_empty(self, path: str) -> None:
    """Successively remove all empty folders starting with `subpath` and
        proceeding "up" through directory tree until reaching the :attr:`root`
        folder.
        """
    try:
      pyfs.tools.remove_empty(self.fs, path)
    except pyfs.errors.ResourceNotFound:
      # Guard against paths that don't exist in the FS.
      return None

  def _makedirs(self, dir_path):
    """Physically create the folder path on disk."""

    try:
      # this is creating a directory, so we use dmode here.
      perms = Permissions.create(self.dmode)
      self.fs.makedirs(dir_path, permissions=perms, recreate=True)

    except pyfs.errors.DirectoryExpected:
      assert self.fs.isdir(dir_path), "expected {} to be a directory".format(
          dir_path)

  def _fs_path(self, k: Union[str, u.HashAddress]) -> Optional[str]:
    """Attempt to determine the real path of a file id or path through successive
    checking of candidate paths.

    """
    # if the input is ALREADY a hash address, pull out the relative path.
    if isinstance(k, u.HashAddress):
      k = k.relpath

    # Check if input was a fs path already.
    if self.fs.isfile(k):
      return k

    # Check if input was an ID.
    filepath = self._hashid_to_path(k)
    if self.fs.isfile(filepath):
      return filepath

    # Could not determine a match.
    return None

  def _hashid_to_path(self, hashid: str) -> str:
    """Build the relative file path for a given hash id.

    """
    paths = self._shard(hashid)
    return pyfs.path.join(*paths)

  def _shard(self, hashid: str) -> str:
    """Shard content ID into subfolders."""
    return u.shard(hashid, self.depth, self.width)

  def _unshard(self, path: str) -> str:
    """Unshard path to determine hash value."""
    if not self.fs.isfile(path):
      raise ValueError("Cannot unshard path. The path {0!r} doesn't exist"
                       "in the filesystem. {1!r}")

    return pyfs.path.splitext(path)[0].replace(os.sep, "")

  def _corrupted(self) -> Iterable[Tuple[Text, u.HashAddress]]:
    """Return generator that yields corrupted files as ``(path, address)``, where
    ``path`` is the path of the corrupted file and ``address`` is the
    :class:`HashAddress` of the expected location.

    """
    for path in self.files():
      with closing(u.Stream(path, fs=self.fs)) as stream:
        hashid = self._computehash(stream)

      expected_path = self._hashid_to_path(hashid)

      if pyfs.path.abspath(expected_path) != pyfs.path.abspath(path):
        yield (
            path,
            u.HashAddress(hashid, expected_path),
        )
