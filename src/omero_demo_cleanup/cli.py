#!/usr/bin/env python
#
# Copyright (C) 2021 University of Dundee.
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


import argparse
from functools import wraps
from typing import Any, Callable

from omero.cli import BaseControl, Parser
from omero.gateway import BlitzGateway
from omero_demo_cleanup.library import (
    choose_users,
    delete_data,
    resource_usage,
    users_by_group,
)

HELP = """Cleanup disk space on OMERO.server """


def gateway_required(func: Callable) -> Callable:
    """
    Decorator which initializes a client (self.client),
    a BlitzGateway (self.gateway), and makes sure that
    all services of the Blitzgateway are closed again.
    """

    @wraps(func)
    def _wrapper(self: Any, *args: Any, **kwargs: Any) -> Callable:
        self.client = self.ctx.conn(*args)
        self.gateway = BlitzGateway(client_obj=self.client)

        try:
            return func(self, *args, **kwargs)
        finally:
            if self.gateway is not None:
                self.gateway.close(hard=False)
                self.gateway = None
                self.client = None  # type: ignore

    return _wrapper


class DemoCleanupControl(BaseControl):
    def _configure(self, parser: Parser) -> None:
        parser.add_login_arguments()
        parser.add_argument(
            "--days",
            "-d",
            type=int,
            default=0,
            help="Do not delete data of users who logged out within recent days. "
            "Default: 0",
        )
        parser.add_argument(
            "--inodes",
            "-i",
            type=int,
            default=0,
            help="How many inodes need to be removed. Default: 0.",
        )
        parser.add_argument(
            "--gigabytes",
            type=int,
            default=0,
            help="How many bytes need to be deleted (in GB). Default: 0.",
        )
        parser.add_argument(
            "--force",
            "-f",
            default=False,
            action="store_true",
            help="Perform the data deletion rather than running in dry-run mode."
            " Default: false.",
        )
        parser.add_argument(
            "--exclude-group",
            "-e",
            help="Members of this group (Name or ID) are excluded from cleanup.",
        )
        parser.set_defaults(func=self.cleanup)

    @gateway_required
    def cleanup(self, args: argparse.Namespace) -> None:
        if args.inodes == 0 and args.gigabytes == 0:
            self.ctx.die(23, "Please specify how much to delete")

        try:
            # Perform data deletion.
            self.ctx.err(
                "Ignoring users who have logged out within the past {} days.".format(
                    args.days
                )
            )

            if args.inodes > 0:
                self.ctx.err(f"Aiming to delete at least {args.inodes:,} files.")

            if args.gigabytes > 0:
                self.ctx.err(
                    "Aiming to delete at least {:,} bytes of data.".format(
                        args.gigabytes
                    )
                )

            exclude = users_by_group(self.gateway, args.exclude_group)
            stats = resource_usage(
                self.gateway, minimum_days=args.days, exclude_users=exclude
            )
            users = choose_users(args.inodes, args.gigabytes * 1000**3, stats)
            self.ctx.err(f"Found {len(users)} user(s) for deletion.")
            for user in users:
                self.ctx.err(
                    'Deleting {} GB of data belonging to "{}" (#{}).'.format(
                        user.size / 1000**3,
                        user.name,
                        user.id,
                    )
                )
                dry_run = not args.force
                if dry_run:
                    self.ctx.err("Despite output, will not actually delete any data.")
                else:
                    self.ctx.err("Running for real: will actually delete data.")
                delete_data(self.gateway, user.id, dry_run=dry_run)
        except KeyboardInterrupt:
            pass  # ignore
