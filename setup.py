import sys
from os import path

from setuptools import find_packages, setup

# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
min_version = (3, 6)
if sys.version_info < min_version:
    error = """
RadTraQ only supports Python 3.x. Please upgrade your Python version.
""".format(*sys.version_info[:2], *min_version)
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [
        line for line in requirements_file.read().splitlines() if not line.startswith('#')
    ]


setup(
    name='RadTraQ',
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': 'dirty-tag',
    },
    description='Python package for weather radar quality tracking',
    author='Adam Theisen',
    author_email='atheisen@anl.gov',
    long_description=readme,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    entry_points={'console_scripts': []},
    include_package_data=True,
    package_data={'radtraq': []},
    install_requires=requirements,
    setup_requires='setuptools_scm',
    license='BSD (3-clause)',
)
