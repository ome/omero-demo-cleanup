#!/usr/bin/env python

# Copyright (C) 2019-2020 University of Dundee & Open Microscopy Environment.
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

from omero.demo_cleanup import UserStats, choose_users

def test_stats():
    # Run tests on "choose_users".

    alice = UserStats(0, 'Alice', 0, 0, 0)
    chloe = UserStats(0, 'Chloe', 0, 1, 0)
    daisy = UserStats(0, 'Daisy', 0, 2, 0)
    elsie = UserStats(0, 'Elsie', 1, 0, 0)
    emily = UserStats(0, 'Emily', 1, 1, 0)
    ethan = UserStats(0, 'Ethan', 1, 2, 0)
    freya = UserStats(0, 'Freya', 2, 0, 0)
    grace = UserStats(0, 'Grace', 2, 1, 0)
    henry = UserStats(0, 'Henry', 2, 2, 0)
    isaac = UserStats(0, 'Isaac', 0, 0, 1)
    jacob = UserStats(0, 'Jacob', 0, 1, 1)
    james = UserStats(0, 'James', 0, 2, 1)
    logan = UserStats(0, 'Logan', 1, 0, 1)
    lucas = UserStats(0, 'Lucas', 1, 1, 1)
    mason = UserStats(0, 'Mason', 1, 2, 1)
    oscar = UserStats(0, 'Oscar', 2, 0, 1)
    poppy = UserStats(0, 'Poppy', 2, 1, 1)
    sofia = UserStats(0, 'Sofia', 2, 2, 1)

    test_users = [alice, chloe, daisy, elsie, emily, ethan,
                  freya, grace, henry, isaac, jacob, james,
                  logan, lucas, mason, oscar, poppy, sofia]

    test_cases = [
        (0, 0, set()),
        (1, 1, {'Henry'}),
        (2, 2, {'Henry'}),
        (6, 0, {'Freya', 'Grace', 'Henry'}),
        (6, 2, {'Freya', 'Grace', 'Henry'}),
        (0, 6, {'Daisy', 'Ethan', 'Henry'}),
        (2, 6, {'Daisy', 'Ethan', 'Henry'}),
        (6, 6, {'Ethan', 'Grace', 'Henry', 'Sofia'}),
        (7, 7, {'Ethan', 'Grace', 'Henry', 'Sofia'}),
        (6, 8, {'Daisy', 'Ethan', 'Grace', 'Henry', 'Sofia'}),
        (6, 9, {'Daisy', 'Ethan', 'Grace', 'Henry', 'Sofia'}),
        (8, 6, {'Ethan', 'Freya', 'Grace', 'Henry', 'Sofia'}),
        (9, 6, {'Ethan', 'Freya', 'Grace', 'Henry', 'Sofia'}),
        (2, 15, {'Chloe', 'Daisy', 'Emily', 'Ethan', 'Grace', 'Henry',
                 'James', 'Mason', 'Sofia'}),
        (6, 15, {'Chloe', 'Daisy', 'Emily', 'Ethan', 'Grace', 'Henry',
                 'James', 'Mason', 'Sofia'}),
        (15, 2, {'Elsie', 'Emily', 'Ethan', 'Freya', 'Grace', 'Henry',
                 'Oscar', 'Poppy', 'Sofia'}),
        (15, 6, {'Elsie', 'Emily', 'Ethan', 'Freya', 'Grace', 'Henry',
                 'Oscar', 'Poppy', 'Sofia'}),
        (13, 13, {'Daisy', 'Emily', 'Ethan', 'Freya', 'Grace', 'Henry',
                  'Mason', 'Poppy', 'Sofia'})]

    case_number = 0

    def test(case_number):
        for file_count, file_size, expected_names in test_cases:
            case_number += 1
            copied_users = list(map(copy, test_users))
            chosen = choose_users(file_count, file_size, copied_users)
            actual_names = set([user.name for user in chosen])
            assert actual_names == expected_names
        return case_number

    case_number = test(case_number)
    test_users.reverse()
    case_number = test(case_number)

