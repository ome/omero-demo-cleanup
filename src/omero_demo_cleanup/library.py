#!/usr/bin/env python

# Copyright (C) 2019-2021 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Delete users' data to free space on the server.
# author: m.t.b.carroll@dundee.ac.uk

import sys
from time import time
from typing import Dict, List, Tuple

import omero
import omero.clients
from omero.cmd import (
    Delete2,
    Delete2Response,
    DiskUsage2,
    DiskUsage2Response,
    HandlePrx,
    LegalGraphTargets,
    LegalGraphTargetsResponse,
)
from omero.gateway import BlitzGateway
from omero.rtypes import rlong
from omero.sys import ParametersI

# If adjusting UserStats, find_worst, choose_users then check with unit tests.


class UserStats:
    # Represents a user and their resource usage.
    # "is_worse_than" defines a strict partial order.

    def __init__(
        self, user_id: int, name: str, count: int, size: int, logout: int
    ) -> None:
        self.id = user_id
        self.name = name
        self.count = count
        self.size = size
        self.logout = logout

    def is_worse_than(self, other: "UserStats") -> bool:
        if (
            other.count > self.count
            or other.size > self.size
            or other.logout < self.logout
        ):
            return False
        return (
            self.count > other.count
            or self.size > other.size
            or self.logout < other.logout
        )


def find_worst(user_stats: List[UserStats]) -> Tuple[List[UserStats], List[UserStats]]:
    # Partition the users into the worst and any remainder.
    worst: List[UserStats] = []
    other: List[UserStats] = []
    for new in user_stats:
        if any([old.is_worse_than(new) for old in worst]):
            other.append(new)
        else:
            other.extend([old for old in worst if new.is_worse_than(old)])
            worst = [old for old in worst if not new.is_worse_than(old)]
            worst.append(new)
    return (worst, other)


def choose_users(
    file_count: int, file_size: int, user_stats: List[UserStats]
) -> List[UserStats]:
    # Iterate through users one by one until enough data would be deleted.
    to_delete: List[UserStats] = []
    reducing_file_count = True
    reducing_file_size = True
    while user_stats:
        if reducing_file_count and file_count <= 0:
            reducing_file_count = False
            for user_stat in user_stats:
                user_stat.count = 0
        if reducing_file_size and file_size <= 0:
            reducing_file_size = False
            for user_stat in user_stats:
                user_stat.size = 0
        if not (reducing_file_count or reducing_file_size):
            break
        (worst, other) = find_worst(user_stats)
        target_user = worst[0]
        user_stats = worst[1:] + other
        to_delete.append(target_user)
        file_count -= target_user.count
        file_size -= target_user.size
    return to_delete


def submit(
    conn: BlitzGateway, request: Delete2, expected: Delete2Response
) -> HandlePrx:
    # Submit a request and wait for it to complete.
    # Returns with the response only if it was of the given type.
    cb = conn.c.submit(request, loops=500)
    try:
        rsp = cb.getResponse()
    finally:
        cb.close(True)

    if not isinstance(rsp, expected):
        conn._closeSession()
        sys.exit(f"unexpected response: {rsp}")
    return rsp


def get_delete_classes(conn: BlitzGateway) -> List[str]:
    # Find the model object types to query and target in deleting users' data.

    delete_classes = []

    rsp = submit(conn, LegalGraphTargets(request=Delete2()), LegalGraphTargetsResponse)

    params = ParametersI()
    params.addId(rlong(0))
    params.page(0, 1)

    for delete_class in rsp.targets:
        if delete_class.endswith("Link"):
            continue
        # TODO: Skipping these only to prevent console output.
        if delete_class in [
            "ome.model.meta.GroupExperimenterMap",
            "ome.model.meta.Namespace",
            "ome.model.meta.ShareMember",
        ]:
            continue
        try:
            conn.getQueryService().projection(
                f"SELECT 1 FROM {delete_class} WHERE details.owner.id = :id",
                params,
            )
            delete_classes.append(delete_class)
        except omero.QueryException:
            # TODO: Suppress console warning output.
            pass
    return delete_classes


def delete_data(conn: BlitzGateway, user_id: int, dry_run: bool = True) -> None:
    # Delete all the data of the given user. Respects the state of dry_run.
    all_groups = {"omero.group": "-1"}
    params = ParametersI()
    params.addId(rlong(user_id))
    delete = Delete2(dryRun=dry_run, targetObjects={})
    for delete_class in get_delete_classes(conn):
        object_ids = []
        for result in conn.getQueryService().projection(
            f"SELECT id FROM {delete_class} WHERE details.owner.id = :id",
            params,
            all_groups,
        ):
            object_id = result[0].val
            object_ids.append(object_id)
        if object_ids:
            delete.targetObjects[delete_class] = object_ids
    if delete.targetObjects:
        submit(conn, delete, Delete2Response)


def find_users(
    conn: BlitzGateway, minimum_days: int = 0
) -> Tuple[Dict[int, str], Dict[int, int]]:
    # Determine which users' data to consider deleting.

    users = {}

    for result in conn.getQueryService().projection(
        "SELECT id, omeName FROM Experimenter", None
    ):
        user_id = result[0].val
        user_name = result[1].val
        if user_name not in ("PUBLIC", "guest", "root", "monitoring"):
            users[user_id] = user_name

    for result in conn.getQueryService().projection(
        "SELECT DISTINCT owner.id FROM Session WHERE closed IS NULL", None
    ):
        user_id = result[0].val
        if user_id in users.keys():
            print(f'Ignoring "{users[user_id]}" (#{user_id}) who is logged in.')
            del users[user_id]

    now = time()

    logouts = {}

    for result in conn.getQueryService().projection(
        "SELECT owner.id, MAX(closed) FROM Session GROUP BY owner.id", None
    ):
        user_id = result[0].val
        if user_id not in users:
            continue

        if result[1] is None:
            # never logged in
            user_logout = 0
        else:
            # note time in seconds since epoch
            user_logout = result[1].val / 1000

        days = (now - user_logout) / (60 * 60 * 24)
        if days < minimum_days:
            print(
                'Ignoring "{}" (#{}) who logged in recently.'.format(
                    users[user_id], user_id
                )
            )
            del users[user_id]

        logouts[user_id] = user_logout
    return users, logouts


def resource_usage(conn: BlitzGateway, minimum_days: int = 0) -> List[UserStats]:
    # Note users' resource usage.
    # DiskUsage2.targetClasses remains too inefficient so iterate.

    user_stats = []
    users, logouts = find_users(conn, minimum_days=minimum_days)
    for user_id, user_name in users.items():
        print(f'Finding disk usage of "{user_name}" (#{user_id}).')
        user = {"Experimenter": [user_id]}
        rsp = submit(conn, DiskUsage2(targetObjects=user), DiskUsage2Response)

        file_count = 0
        file_size = 0

        for who, usage in rsp.totalFileCount.items():
            if who.first == user_id:
                file_count += usage
        for who, usage in rsp.totalBytesUsed.items():
            if who.first == user_id:
                file_size += usage

        if file_count > 0 or file_size > 0:
            user_stats.append(
                UserStats(user_id, user_name, file_count, file_size, logouts[user_id])
            )
    return user_stats


def perform_delete(
    conn: BlitzGateway,
    minimum_days: int = 0,
    excess_file_count: int = 0,
    excess_file_size: int = 0,
    dry_run: bool = True,
) -> None:
    # Perform data deletion.
    stats = resource_usage(conn, minimum_days=minimum_days)
    users = choose_users(excess_file_count, excess_file_size, stats)
    print(f"Found {len(users)} user(s) for deletion.")
    for user in users:
        print(
            'Deleting {} GB of data belonging to "{}" (#{}).'.format(
                user.size / 1000 ** 3,
                user.name,
                user.id,
            )
        )
        delete_data(conn, user.id, dry_run=dry_run)


def main() -> None:

    with omero.cli.cli_login() as cli:
        conn = omero.gateway.BlitzGateway(client_obj=cli.get_client())
        try:
            perform_delete(conn)
        except KeyboardInterrupt:
            pass  # ignore
        finally:
            conn.close()


if __name__ == "__main__":
    main()
