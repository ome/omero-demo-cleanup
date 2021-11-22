#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from omero.cli import CLI
from omero_demo_cleanup.cli import HELP, DemoCleanup

try:
    register("demo-cleanup", DemoCleanup, HELP) # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("demo-cleanup", UploadControl, HELP)
        cli.invoke(sys.argv[1:])
