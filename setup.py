#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["pandas>=0.20", "iso8601", "textbisect"]

setup_requirements = []

test_requirements = []

setup(
    name="htimeseries",
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Hydrological and meteorological timeseries",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    packages=find_packages(include=["htimeseries"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/openmeteo/htimeseries",
    version="1.1.2",
    zip_safe=False,
)
