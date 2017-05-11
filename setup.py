from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='truckfinder',
    version='0.0.1',
    description='A web app for tracking Ford F-150 pricing and availability.',
    long_description=long_description,
    author="Peter Stratton",
    author_email='stratton.peter@gmail.com',
    zip_safe=False,
    url='https://github.com/peter-stratton/truckfinder',
    classifiers=[
        'Intended Audience :: Peter Stratton',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6'
    ],
    packages=['truckfinder'],
    install_requires=['flask',
                      'flask-sqlalchemy',
                      'flask-migrate',
                      'flask-env',
                      'psycopg2',
                      'requests'],
    test_suite='tests'
)
