#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wininst upload -r pypi')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='django-rest-surveys',
    version='0.1.0',
    description='A RESTful backend for giving surveys.',
    long_description=readme,
    author='Designlab',
    author_email='hello@trydesignlab.com',
    url='https://github.com/danxshap/django-rest-surveys',
    packages=['rest_surveys'],
    package_data={'': ['LICENSE']},
    package_dir={'rest_surveys': 'rest_surveys'},
    install_requires=['Django', 'django-inline-ordering'],
    license=license,
)
