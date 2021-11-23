#!/usr/bin/env python

import sys

from omero.cli import CLI
from omero_demo_cleanup.cli import HELP, DemoCleanupControl

try:
    register("demo-cleanup", DemoCleanupControl, HELP)  # type: ignore # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("demo-cleanup", DemoCleanupControl, HELP)
        cli.invoke(sys.argv[1:])
