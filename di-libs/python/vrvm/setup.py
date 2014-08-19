#!/usr/bin/env python
"""Moving towards making vrvm a formal package.

til we finish the package migration process, this file is
useful to manually track python dependencies.

"""
from distutils.core import setup

setup(
  name='vrvm',
  requires=[
    'MySQL-python>=1.2.3c1',
    'argparse>=1.2.1',
    'boto>=2.27.0',
    'lockfile>=0.9.1',
    'psycopg2>=2.5.1',
    'pycurl>=7.19.0',  # might not be necessary?
    'requests==1.1.0',  # might not be necessary?
    's3cmd==1.0.1',  # might not be necessary?
  ],
)

