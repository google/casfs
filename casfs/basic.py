"""Basic namespace; examples and tests.

"""

import os
from contextlib import closing
from io import StringIO

import fs
from fs import memoryfs

from casfs import CASFS


def persist(filesystem: fs.base.FS):
  """Add a docstring."""
  # Create our content addressable store.
  f = CASFS(filesystem, depth=2, width=2, algorithm='sha256')

  # Create some content.
  a = StringIO('a content')
  b = StringIO('b content')

  # Put both in the filesystem.
  ak = f.put(a)
  bk = f.put(b)

  # You can get the key back out with various paths.
  assert f.get(ak) == ak
  assert f.get(ak.id) == ak
  assert f.get(ak.relpath) == ak

  # Passing in junk results in junk.
  assert f.get('random') == None

  rt_a = None
  with closing(f.open(ak.id)) as a_file:
    print("Reading a")
    rt_a = a_file.read()

  # the file yields its goodies!
  assert rt_a == b'a content'

  # What's in the FS?
  filesystem.tree()

  # all files:
  print(list(f.files()))

  # all folders:
  print(list(f.folders()))

  # total number of
  print("{} files in the hashfs.".format(f.count()))
  print("{} bytes stored in the hashfs.".format(f.size()))

  f.delete(ak)
  f.delete(bk)

  print("{} files in the hashfs AFTER delete.".format(f.count()))
  print("{} bytes stored in the hashfs AFTER delete.".format(f.size()))

  print("Does the deleted file exist? {}".format(f.exists(ak)))
  f.repair()
  filesystem.tree()


if __name__ == '__main__':
  # in-memory:

  persist(memoryfs.MemoryFS())

  # local
  persist(fs.open_fs('~/.modeldb', create=True))

  bucket = os.environ.get("BUCKET_NAME")
  gcsfs = fs.open_fs("gs://{}/cas?strict=False".format(bucket))
  persist(gcsfs)
