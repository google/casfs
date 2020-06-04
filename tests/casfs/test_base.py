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
"""Basic namespace; examples and tests.


TODO - handle strings for 'put'

"""

from contextlib import closing
from io import StringIO

import casfs.util as u
from casfs import CASFS
from fs.copy import copy_fs
from fs.memoryfs import MemoryFS
from fs.opener.errors import UnsupportedProtocol

import pytest


@pytest.fixture
def mem():
  return MemoryFS()


@pytest.fixture
def memcas(mem):
  return CASFS(mem)


def test_put_get(memcas):
  """Test basic operations."""

  # Create some content and put it into the filesystem.
  a = StringIO('content')
  ak = memcas.put(a)

  # You can get the key back out with various paths.
  assert memcas.get(ak) == ak
  assert memcas.get(ak.id) == ak
  assert memcas.get(ak.relpath) == ak
  assert memcas.exists(ak)
  assert ak in memcas

  with closing(memcas.open(ak)) as a_file:
    rt_a = a_file.read()

    # Boom, content round-trips.
    assert rt_a == b'content'


def test_get_missing(memcas):
  # Passing in junk results in junk.
  assert memcas.get('random') == None


def test_delete(memcas):
  # Create some content and put it into the filesystem.
  s = 'content'
  a = StringIO(s)
  ak = memcas.put(a)
  assert memcas.count() == 1
  assert memcas.size() == len(s.encode('utf-8'))
  assert memcas.exists(ak)

  memcas.delete(ak)
  assert memcas.count() == 0
  assert memcas.size() == 0
  assert not memcas.exists(ak)

  # deleting again is a no-op:
  assert memcas.delete(ak) is None

  # You'll get an error if you attempt to open a closed file.
  with pytest.raises(IOError):
    memcas.open(ak)


def test_key_matches_content(memcas):
  """Adding the same thing to the store twice """
  ak = memcas.put(StringIO('A'))
  bk = memcas.put(StringIO('A'))

  assert ak == bk

  # deleting ak means bk is no longer available.
  assert memcas.exists(bk)
  memcas.delete(ak)
  assert not memcas.exists(bk)


def test_files_folders_repair(memcas):
  ak = memcas.put(StringIO('A'))
  bk = memcas.put(StringIO('B'))
  ck = memcas.put(StringIO('C'))

  # The sequence of files returns from files() consists of the set of all
  # relative paths inside the filesystem.
  assert set(memcas.files()) == {ak.relpath, bk.relpath, ck.relpath}

  # memcas itself is iterable!
  assert list(memcas) == list(memcas.files())

  # using a NEW CASFS instance with different settings for width and depth than the original
  newfs = CASFS(memcas.fs, width=7, depth=1)

  # guard against the defaults changing and invalidating the test.
  #
  # TODO I am quite suspicious of this test. I don't think we should store all
  # the is_duplicate info and the relative path inside of the key; it's not
  # really relevant. But maybe you do need to go get the actual system path.
  # Think about this.
  assert newfs.width != memcas.width
  assert newfs.depth != memcas.depth
  assert newfs.count() == memcas.count()
  assert newfs.size() == memcas.size()
  assert newfs.get(ak) == memcas.get(ak)

  # Then we repair, which should muck with stuff.
  old_folders, old_files = set(newfs.folders()), set(newfs.files())
  newfs.repair()
  new_folders, new_files = set(newfs.folders()), set(newfs.files())

  # folder names and file names were modified.
  assert old_folders != new_folders
  assert old_files != new_files

  # gets still work!
  assert newfs.get(ak) == memcas.get(ak)


def test_folders(memcas):
  ak = memcas.put(StringIO('A'))
  bk = memcas.put(StringIO('B'))

  # almost certainly true, since we shard out the folders.
  assert len(list(memcas.folders())) == 2


def test_repair_corruption():
  fs1 = CASFS(MemoryFS(), width=2, depth=2)
  fs2 = CASFS(MemoryFS(), width=7, depth=1)

  # populate EACH with the same kv pairs, but structured different ways inside
  # the filesystem.
  ak1, bk1 = fs1.put(StringIO('A')), fs1.put(StringIO('B'))
  ak2, bk2 = fs2.put(StringIO('A')), fs2.put(StringIO('B'))

  # fs2 of course only has two items in it.
  assert fs2.count() == 2

  # Now copy all of fs1 into fs2...
  copy_fs(fs1.fs, fs2.fs)

  # and note that it now has two copies of each item in the CAS.
  assert fs2.count() == 4

  # Repair should kill the duplicates.
  fs2.repair()
  assert fs2.count() == 2

  # fs2 itself is an iterable and has a length.
  assert len(fs2) == 2


def test_internals():
  fs1 = CASFS(MemoryFS(), width=2, depth=2)
  fs2 = CASFS(MemoryFS(), width=7, depth=1)
  ak1 = fs1.put(StringIO('A'))

  # removing a path that doesn't exist should be a no-op.
  assert fs2._remove_empty(ak1.relpath) == None

  # if internally you try to make a directory that extends some non-directory
  # thing, some existing file, you'll see an error.
  with pytest.raises(AssertionError):
    fs1._makedirs(ak1.relpath + "/cake")

  # Unshard expects a path that actually exists.
  with pytest.raises(ValueError):
    fs1._unshard("random_path")


def test_alternate_fs():
  # temp:// creates a temporary filesystem fs.
  fs = CASFS("temp://face")
  ak = fs.put(StringIO('A'))

  rt = None
  with closing(fs.open(ak)) as f:
    rt = f.read()

    # Boom, content round-trips!
    assert rt == b'A'

  with pytest.raises(UnsupportedProtocol):
    fs = CASFS("random://face")

  with pytest.raises(Exception):
    fs = CASFS(10)


def test_syspath(memcas):
  # temp:// creates a temporary filesystem fs.
  fs = CASFS("temp://face")
  ak = fs.put(StringIO('A'))
  ak2 = memcas.put(StringIO('A'))

  rt = None
  with closing(fs.open(ak)) as f:
    rt = f.read()

  # it's possible in a filesystem-based FS to go get the ACTUAL path and use
  # that to read data out.
  with open(u.syspath(fs.fs, ak.relpath)) as f2:
    # the data should be the same.
    rt2 = f2.read()
    assert rt2.encode('utf-8') == rt

  # this trick does not work on a MemoryFS based CAS. It returns None to show
  # us that this isn't a thing.
  assert u.syspath(memcas.fs, ak.relpath) == None


def test_stream(mem):
  # streams have to be something openable, for now... nothing primitive works.
  with pytest.raises(ValueError):
    u.Stream(10)

  # Looking like a path isn't enough. You have to pass the internal test of the
  # filesystem.
  with pytest.raises(ValueError):
    u.Stream("cake", fs=mem)
