#!/usr/bin/env python
import sys

from os import path
from functools import partial

from setuptools import setup, find_packages

name = 'tinbox-mx'  # PyPI name
package_name = 'mx'  # Python module name
package_path = 'src'  # Where does the package live?

here = path.dirname(path.abspath(__file__))

# Add src dir to path
sys.path.append(package_path)

# Get the long description from the relevant file
long_description = None

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def get_version() -> "version string":
    """
    Get the version from a version module inside our package. This is
    necessary since we import our main modules in package/__init__.py,
    which will cause ImportErrors if we try to import package/version.py
    using the regular import mechanism.

    :return: Formatted version string
    """
    version = {}

    version_file = path.join(package_path, package_name, '__init__.py')

    # exec the version module
    with open(version_file) as fp:
        exec(fp.read(), version)

    # Call the module function 'get_version'
    return version['get_version']()


setup(
    name=name,
    version=get_version(),
    author='Jonas Lundberg',
    author_email='jonas@5monkeys.se',
    url='https://github.com/5monkeys/tinbox-mx',
    license='MIT',
    package_dir={'': package_path},
    packages=find_packages(package_path),
    entry_points={
        'console_scripts': [
            'mx = mx.cli.command:Interface',
        ]
    },
    install_requires=[
        'tinbox-client==1.0a1',
        'chardet>=2.3.0',
        'docopt>=0.6.2'
    ]
)
