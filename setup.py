#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src)

name = 'mx'
version = __import__(name).__version__

setup(
    name=name,
    version=version,
    author='Jonas Lundberg',
    author_email='jonas@5monkeys.se',
    package_dir={'': 'src'},
    packages=find_packages(exclude=['_*']),
    entry_points={
        'console_scripts': [
            'mx = mx.cli.command:Interface',
        ]
    },
    install_requires=[
        'tinbox-client==0.1b5',
        'chardet>=2.3.0',
        'docopt>=0.6.2'
    ]
)
