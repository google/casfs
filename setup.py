from setuptools import setup, find_packages

with open('README.md') as f:
  readme = f.read()


def with_versioneer(f, default=None):
  """Attempts to execute the supplied single-arg function by passing it
versioneer if available; else, returns the default.

  """
  try:
    import versioneer
    return f(versioneer)
  except ModuleNotFoundError:
    return default


REQUIRED_PACKAGES = ["fs", "fs-gcsfs"]

setup(
    name='casfs',
    version=with_versioneer(lambda v: v.get_version()),
    cmdclass=with_versioneer(lambda v: v.get_cmdclass(), {}),
    description="Content-Addressable filesystem over Pyfilesystem2.",
    long_description=readme,
    python_requires='>=3.5.3',
    author='Blueshift Team',
    author_email='samritchie@google.com',
    url='https://team.git.corp.google.com/blueshift/casfs',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
)
