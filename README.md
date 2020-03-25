# CASFS

CASFS is Blueshift's content-addressable filestore library, built on
pyfilesystem2. CASFS was inspired by hashfs.

This page covers the details of how to

- Use the `casfs` library in your project, both in and out of an isolated
  [Caliban](http://go/caliban) environment
- Develop against `casfs`, run its tests and contribute code

## Installing CasFS

The [Installing CasFS](http://go/casfs#installing-casfs) section of CasFS's [g3doc
documentation](http://go/casfs#installing-casfs) describes at length how to require
the `casfs` library in your project, in and out of Docker containers.
Head [to those docs](http://go/casfs#installing-casfs) for the full story.

Here's a short version, since you made it here.

`casfs` is hosted on [Nest's artifactory
instance](https://artifactory2.nestlabs.com/). This is currently the easiest way
to make `casfs` accessible inside of Docker containers.

Run this command to install `casfs` using `pip`:

```bash
pip install casfs --extra-index-url https://artifactory2.nestlabs.com/artifactory/api/pypi/pypi-local/simple
```

You can also add the artifactory instance to your permanent list of indexes to
search by adding this line to `~/.pip/pip.conf`:

```yaml
[global]
extra-index-url = https://artifactory2.nestlabs.com/artifactory/api/pypi/pypi-local/simple
```

After this, you can install `casfs` with the usual `pip` incantations:

```
pip install casfs
```

### Installing from Git-on-Borg Source

If you want to install the library directly from source, you can use `pip` to
pull from the CasFS git repository directly:

```bash
pip install -e git+sso://team/blueshift/casfs#egg=casfs
```

Note that this will *not* work inside of a Docker container or
[Caliban](http://go/caliban) build, as the container doesn't have the
credentials required to access `sso://` URLs.

If you're want to install a specific branch, append it to the repo URL like
this:

```bash
pip install -e git+sso://team/blueshift/casfs@{{USERNAME}}/my_branch#egg=casfs
```

## Developing in CasFS

So you want to add some code to `casfs`. Excellent!

### Checkout and pre-commit hooks

First, check out the repo:

```
git clone sso://team/blueshift/casfs && cd casfs
```

Then run this command to install a special pre-commit hook that Gerrit needs to
manage code review properly. You'll only have to run this once.

```bash
f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f) ; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg ; chmod +x $f
```

We use [pre-commit](https://pre-commit.com/) to manage a series of git
pre-commit hooks for the project; for example, each time you commit code, the
hooks will make sure that your python is formatted properly. If your code isn't,
the hook will format it, so when you try to commit the second time you'll get
past the hook.

All hooks are defined in `.pre-commit-config.yaml`. To install these hooks,
install `pre-commit` if you don't yet have it. I prefer using [pipx](https://github.com/pipxproject/pipx) so that `pre-commit` stays globally available.

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

### Aliases

You might find these aliases helpful when developing in CasFS:

```
[alias]
	review = "!f() { git push origin HEAD:refs/for/${1:-master}; }; f"
	amend  = "!f() { git add . && git commit --amend --no-edit; }; f"
```

### New Feature Workflow

To add a new feature, you'll want to do the following:

- create a new branch off of `master` with `git checkout -b my_branch_name`.
  Don't push this branch yet!
- run `make build` to set up a virtual environment inside the current directory.
- periodically run `make pytest` to check that your modifications pass tests.
- to run a single test file, run the following command:

```bash
env/bin/pytest tests/path/to/your/test.py
```

You can always use `env/bin/python` to start an interpreter with the correct
dependencies for the project.

When you're ready for review,

- commit your code to the branch (multiple commits are fine)
- run `git review` in the terminal. (This is equivalent to running `git push
  origin HEAD:refs/for/master`, but way easier to remember.)

The link to your pull request will show up in the terminal.

If you need to make changes to the pull request, navigate to the review page and
click the "Download" link at the bottom right:

![](https://screenshot.googleplex.com/4BP8v3TWq4R.png)

Copy the "checkout" code, which will look something like this:

```bash
git fetch "sso://team/blueshift/casfs" refs/changes/87/670987/2 && git checkout FETCH_HEAD
```

And run that in your terminal. This will get you to a checkout with all of your
code. Make your changes, then run `git amend && git review` to modify the pull
request and push it back up. (Remember, these are aliases we declared above.)

## Publishing CasFS

`casfs` is hosted on [Nest's artifactory
instance](https://artifactory2.nestlabs.com/).

The first step to publishing `casfs` is to follow the instructions at [this
guide](http://go/nest-pypi-local#generating-your-api-key). Once you:

- Log in to [Artifactory](https://artifactory2.nestlabs.com/)
- Generate your API Key
- create `~/.pypirc` as described in the guide

You're ready to publish.

- First, run `make build` to get your virtual environment set up.
- Make sure that you're on the master branch!
- add a new tag, with `git tag 0.2.3` or the equivalent
- run `make release` to package and push `casfs` to artifactory and all relevant
  repositories.

## Trouble?

Get in touch with [samritchie@x.team](mailto:samritchie@x.team).
