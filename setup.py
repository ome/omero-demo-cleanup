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

from setuptools import setup


def get_long_description() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "README.rst")) as f:
        long_description = f.read()
    return long_description


long_description = get_long_description()

setup(
    name="omero-demo-cleanup",
    version="0.2.2.dev0",
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
    install_requires=["omero-py>=5.6.0"],
    zip_safe=True,
    keywords=["OMERO.CLI", "plugin"],
    long_description=long_description,
    url="https://github.com/ome/omero-demo-cleanup/",
)
