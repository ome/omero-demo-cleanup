.. image:: https://github.com/ome/omero-demo-cleanup/workflows/OMERO/badge.svg
   :target: https://github.com/ome/omero-demo-cleanup/actions

.. image:: https://badge.fury.io/py/omero-demo-cleanup.svg
    :target: https://badge.fury.io/py/omero-demo-cleanup

OMERO demo cleanup
==================

This OMERO command-line plugin allows you to compute the space per user, find
the users with the biggest amount of data and free disk space on a server

To generate the list of users which data must be deleted to free 300GB on the
system without running the deletion::

    $ omero demo-cleanup --gigabytes 300

To generate the list of users which data must be deleted to free 300GB on the
system and running the deletion (WARNING: data belonging to these users will
be removed permanently)::

    $ omero demo-cleanup --gigabytes 300 --force
