#!/usr/bin/env python
import sys
from os import path
from setuptools import setup, find_packages

src = path.join(path.dirname(path.abspath(__file__)), 'src')
print('append src', src)
sys.path.append(src)

name = 'mx'
version = __import__(name).__version__

import os
os.chdir(src)

setup(
    name=name,
    version=version,
    author='Jonas Lundberg',
    author_email='jonas@5monkeys.se',
    packages=find_packages(exclude=['_*']),
    entry_points={
        'console_scripts': [
            'mx = mx.cli.command:Interface',
        ]
    },
    install_requires=[
        'chardet>=2.3.0',
        'docopt>=0.6.2'
    ]
)
