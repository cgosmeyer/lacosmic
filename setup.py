#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(name = 'lacosmic',
      description = 'LACOSMIC IRAF Python wrapper',
      author = 'C.M. Gosmeyer',
      url = 'https://github.com/cgosmeyer/lacosmic',
      packages = find_packages(),
      install_requires = ['astropy', 'numpy']
     )