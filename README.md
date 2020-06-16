# CASFS

[![Build status](https://img.shields.io/travis/google/casfs/master.svg?maxAge=3600)](http://travis-ci.org/google/casfs)
[![Codecov branch](https://img.shields.io/codecov/c/github/google/casfs/master.svg?maxAge=3600)](https://codecov.io/github/google/casfs)
[![readthedocs](https://img.shields.io/readthedocs/casfs?maxAge=3600)](https://casfs.readthedocs.io/en/latest/?badge=latest)
[![Latest version](https://img.shields.io/pypi/v/casfs?maxAge=3600)](https://pypi.org/project/casfs)

CASFS is a content-addressable filestore library, built on
[pyfilesystem2](https://github.com/PyFilesystem/pyfilesystem2). CASFS was
inspired by [hashfs](https://github.com/dgilland/hashfs).

## Installation and Usage

Install CASFS via [pip](https://pypi.org/project/casfs/):

```bash
pip install casfs
```

Full documentation for CASFS lives at [Read The
Docs](https://casfs.readthedocs.io/en/latest).

## Disclaimer

This is a research project, not an official Google product. Expect bugs and
sharp edges. Please help by trying out Caliban, [reporting
bugs](https://github.com/google/caliban/issues), and letting us know what you
think!

## Citing CASFS

If Caliban helps you in your research, pleae consider citing the repository:

```
@software{casfs2020github,
  author = {Sam Ritchie},
  title = {{CASFS}: Content-addressable filesystem abstraction for Python.},
  url = {http://github.com/google/casfs},
  version = {0.1.0},
  year = {2020},
}
```

In the above bibtex entry, names are in alphabetical order, the version number
is intended to be that of the latest tag on github, and the year corresponds to
the project's open-source release.

## License

Copyright 2020 Google LLC.

Licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
