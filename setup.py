from os import path
from setuptools import setup, find_packages
import sys


# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
min_version = (3, 6)
#if sys.version_info < min_version:
#    print(sys.version_info)
#    sys.exit('Wrong Version')

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]


setup(
    name='TestRepo',
    description="Package for working with atmospheric time series datasets",
    author="Adam Theisen",
    author_email='atheisen@anl.gov',
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points={'console_scripts': []},
    include_package_data=True,
    package_data={'testrepo': []},
    install_requires=requirements,
    license="BSD (3-clause)",
)
