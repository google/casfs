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
from setuptools import setup, find_packages


def with_versioneer(f, default=None):
  """Attempts to execute the supplied single-arg function by passing it
versioneer if available; else, returns the default.

  """
  try:
    import versioneer
    return f(versioneer)
  except ModuleNotFoundError:
    return default


def readme():
  try:
    with open('README.md') as f:
      return f.read()
  except Exception:
    return None


REQUIRED_PACKAGES = ["fs", "fs-gcsfs"]

setup(
    name='casfs',
    version=with_versioneer(lambda v: v.get_version()),
    cmdclass=with_versioneer(lambda v: v.get_cmdclass(), {}),
    description="Content-Addressable filesystem over Pyfilesystem2.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    python_requires='>=3.5.3',
    author='Sam Ritchie',
    author_email='samritchie@google.com',
    url='https://github.com/google/casfs',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
)
