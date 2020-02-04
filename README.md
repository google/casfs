# CASFS

CAS-FS is Blueshift's content-addressable filestore library, built on
pyfilesystem2. CASFS was inspired by hashfs.

## Installing CAS-FS

To use the library, simply install off of master.

```bash
pip install -e git+sso://team/blueshift/casfs#egg=casfs
```

If you're developing and want to install a specific branch, append it to the
repo URL:

```bash
pip install -e git+sso://team/blueshift/casfs@branchname#egg=casfs
```

# Getting Started

What lives here?

## Code Review

To push code,

First run this:

```sh
f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f) ; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg ; chmod +x $f
```

-   create a branch
-   work!
-   commit
-   `git push origin HEAD:refs/for/master`

More info to file on the process:
https://www.gerritcodereview.com/user-review-ui.html

And info from internally on how code review works:
https://g3doc.corp.google.com/company/teams/gerritcodereview/users/intro-codelab.md?cl=head#create-a-change

## Testing

This is how to configure tests.

https://g3doc.corp.google.com/devtools/kokoro/g3doc/userdocs/general/gob_scm.md?cl=head

## Developing

Run this to get all of the nice language-checking goodies.

```sh
pip install 'python-language-server[all]'
```

## Trouble?

Get in touch with [samritchie@google.com](mailto:samritchie@google.com).
