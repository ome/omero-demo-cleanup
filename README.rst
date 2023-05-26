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

To ignore users who's data whose data must not be deleted, you can Tag those users
and specify the `Tag` or parent `Tag Group` by `Name` or `ID`.
This is enabled by default using a Tag named "NO DELETE".
So it is preferable to Tag users on the server with a `Tag` named "NO DELETE" or create
a `Tag Group` named "NO DELETE" containing Tags linked to users.

    # Add a Tag to a User via CLI (not possible to see this in the clients)
    $ omero obj new ExperimenterAnnotationLink child=TagAnnotation:123 parent=Experimenter:52

    # Choose a non-default Tag or Tag Group (by ID or Name) to ignore the tagged users
    $ omero demo-cleanup --gigabytes 300 --ignore-tag "Tag Name"

You can also specify individual users by ID or user name, e.g:

    --ignore-users 123,user-1,ben,234

To generate the list of users which data must be deleted to free 300GB on the
system and running the deletion (WARNING: data belonging to these users will
be removed permanently)::

    $ omero demo-cleanup --gigabytes 300 --force
