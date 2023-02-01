#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#
import os
import sys
from setuptools import find_packages, setup
from ghconn import __version__  # NOQA



with open("README.md") as f:
    long_description = f.read()


classifiers = [
    "Programming Language :: Python",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3 :: Only",
]


setup(
    name="elasticsearch-connectors",
    version=__version__,
    packages=find_packages(),
    description=("Elastic Search Connectors."),
    long_description=long_description,
    author="Ingestion Team",
    author_email="tarek@ziade.org",
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=['aiohttp', 'elasticsearch-connectors'],
)
