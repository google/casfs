# CASFS

[![Build status](https://img.shields.io/travis/google/casfs/master.svg?maxAge=3600)](http://travis-ci.org/google/casfs)
[![Codecov branch](https://img.shields.io/codecov/c/github/google/casfs/master.svg?maxAge=3600)](https://codecov.io/github/google/casfs)
[![Latest version](https://img.shields.io/pypi/v/casfs?maxAge=3600)](https://pypi.org/project/casfs)

CASFS is a content-addressable filestore library, built on
[pyfilesystem2](https://github.com/PyFilesystem/pyfilesystem2). CASFS was
inspired by [hashfs](https://github.com/dgilland/hashfs).

This page covers the details of how to

- Use the `casfs` library in your project, both in and out of an isolated Docker
  environment
- Develop against `casfs`, run its tests and contribute code


## Installation and Usage

We'll add more here once we're staged on Github and can get proper links to
generated docs.

This is a research project, not an official Google product. Expect bugs and
sharp edges. Please help by trying out CASFS, [reporting
bugs](https://github.com/google/casfs/issues), and letting us know what you
think!

## Developing in CASFS

So you want to add some code to CASFS. Excellent!

We use [pre-commit](https://pre-commit.com/) to manage a series of git
pre-commit hooks for the project; for example, each time you commit code, the
hooks will make sure that your python is formatted properly. If your code isn't,
the hook will format it, so when you try to commit the second time you'll get
past the hook.

All hooks are defined in `.pre-commit-config.yaml`. To install these hooks,
install `pre-commit` if you don't yet have it. I prefer using
[pipx](https://github.com/pipxproject/pipx) so that `pre-commit` stays globally
available.

```bash
pipx install pre-commit
```

Then install the hooks with this command:

```bash
pre-commit install
```

Now they'll run on every commit. If you want to run them manually, you can run either of these commands:

```bash
pre-commit run --all-files

# or this, if you've previously run `make build`:
make lint
```

## Publishing CASFS

- First, run `make build` to get your virtual environment set up.
- Make sure that you're on the master branch!
- add a new tag, with `git tag 0.2.3` or the equivalent
- run `make release` to push the latest code and tags to all relevant
  repositories.

## Citing CASFS

To cite this repository:

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
