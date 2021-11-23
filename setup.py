#!/usr/bin/env python
#
# Copyright (c) 2021 University of Dundee.
# All rights reserved.
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import os
import sys

from setuptools import setup
from setuptools.command.test import test as test_command


class PyTest(test_command):
    user_options = [
        ("test-path=", "t", "base dir for test collection"),
        ("test-ice-config=", "i", "use specified 'ice config' file instead of default"),
        ("test-pythonpath=", "p", "prepend 'pythonpath' to PYTHONPATH"),
        ("test-marker=", "m", "only run tests including 'marker'"),
        ("test-no-capture", "s", "don't suppress test output"),
        ("test-failfast", "x", "Exit on first error"),
        ("test-verbose", "v", "more verbose output"),
        ("test-quiet", "q", "less verbose output"),
        ("junitxml=", None, "create junit-xml style report file at 'path'"),
        ("pdb", None, "fallback to pdb on error"),
    ]

    def initialize_options(self) -> None:
        test_command.initialize_options(self)
        self.test_pythonpath = None
        self.test_string = None
        self.test_marker = None
        self.test_path = "test"
        self.test_failfast = False
        self.test_quiet = False
        self.test_verbose = False
        self.test_no_capture = False
        self.junitxml = None
        self.pdb = False
        self.test_ice_config = None

    def finalize_options(self) -> None:
        test_command.finalize_options(self)
        self.test_args = [self.test_path]
        if self.test_string is not None:
            self.test_args.extend(["-k", self.test_string])
        if self.test_marker is not None:
            self.test_args.extend(["-m", self.test_marker])
        if self.test_failfast:
            self.test_args.extend(["-x"])
        if self.test_verbose:
            self.test_args.extend(["-v"])
        if self.test_quiet:
            self.test_args.extend(["-q"])
        if self.junitxml is not None:
            self.test_args.extend(["--junitxml", self.junitxml])
        if self.pdb:
            self.test_args.extend(["--pdb"])
        self.test_suite = True
        if "ICE_CONFIG" not in os.environ and self.test_ice_config is not None:
            os.environ["ICE_CONFIG"] = self.test_ice_config

    def run_tests(self) -> None:
        if self.test_pythonpath is not None:
            sys.path.insert(0, self.test_pythonpath)
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


def get_long_description() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "README.rst")) as f:
        long_description = f.read()
    return long_description


long_description = get_long_description()

setup(
    name="omero-demo-cleanup",
    version="0.1.0.dev0",
    packages=["omero_demo_cleanup", "omero.plugins"],
    package_dir={"": "src"},
    description="Plugin for managing the disk space on the demo server.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v2 " "or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="The Open Microscopy Team",
    author_email="",
    python_requires=">=3.6",
    cmdclass={"test": PyTest},
    install_requires=["omero-py>=5.6.0"],
    zip_safe=True,
    keywords=["OMERO.CLI", "plugin"],
    long_description=long_description,
    url="https://github.com/ome/omero-demo-cleanup/",
    tests_require=["pytest"],
)
