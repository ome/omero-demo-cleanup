#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


import sys
from typing import Any, Callable, List

from omero.cli import BaseControl
from omero_demo_cleanup.library import resource_usage, choose_users, delete_data


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
        parser.add_argument(
            "--days", "-d", type=int, default=0,
            "Do not delete data of users who logged out within recent days. "
            "Default: 0")
        parser.add_argument(
            "--inodes", "-i", type=int, default=0,
            "How many inodes need to be removed. Default: 0.")
        parser.add_argument(
            "--gigabytes", "-g", type=int, default=0,
            "How many bytes need to be deleted (in GB). Default: 0.")
        parser.add_argument(
            "--force", "-f", default=False, action="store_true",
            "Perform the data deletion rather than running in dry-run mode."
            " Default: false.")
        parser.set_defaults(func=self.cleanup)
        parser.add_login_arguments()

    @gateway_required
    def cleanup(self, args: argparse.Namespace) -> None:

        # Leave this as True except when running the script for real.
        dry_run = not ns.force
        
        if args.inodes == 0 and args.gigabytes == 0:
            self.ctx.die(23, "Please specify how much to delete")

        try:
            # Perform data deletion.
            self.ctx.info(
                'Ignoring users who have logged out within the past {} days.'
                 .format(minimum_days))

            if args.inodes > 0:
                self.ctx.info('Aiming to delete at least {:,} files.'
                      .format(args.inodes))

            if args.gigabytes > 0:
                self.ctx.info('Aiming to delete at least {:,} bytes of data.'
                      .format(args.gigabytes))

            stats = resource_usage(self.conn, minimum_days=args.days)
            users = choose_users(args.inodes, args.gigabytes * 1000**3)
            self.ctx.info('Found {} user(s) for deletion.'.format(len(users)))
            for user in users:
                self.ctx.info(
                    'Deleting {} GB of data belonging to "{}" (#{}).'.format(
                     user.size / 1000**3, user.name, user.id,))
                dry_run = not ns.force
                if dry_run:
                    self.ctx.info(
                        'Despite output, will not actually delete any data.')
                else:
                    self.ctx.info(
                        'Running for real: will actually delete data.')
                delete_data(self.gateway, user.id, dry_run=dry_run)
        except KeyboardInterrupt:
            pass  # ignore
