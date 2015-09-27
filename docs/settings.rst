..  Copyright (C) 2015 Jessica Tallon & Matt Molyneaux

    This file is part of Inboxen.

    Inboxen is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Inboxen is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Inboxen  If not, see <http://www.gnu.org/licenses/>.

================
The Setting File
================

The settings file is required to set basic settings for the inboxen instance.
It contains some secret information such as the ``secret_key``, you
should ensure the permissions are set correctly and also that this file is kept
safe as without it sessions, cookie storage and along with other things rely on
this [0]_.

The inboxen settings file can be located in several places on a system, it will
use the first one it finds. Inboxen looks for the files in this order:

1. The path specified in the enviroment variable: ``INBOXEN_CONFIG``
2. ~/.config/inboxen/settings.ini
3. settings.ini (inside the base directory of the inboxen project)

If you're familiar with Django settings and would like to use your own settings
module, you can set ``DJANGO_SETTINGS_MODULE`` in the usual way [1]_.


Minimum Development Configuration
=================================

To hit the ground running, the minimum you need to setup a development instance
is::

    [general]
    secret_key = something-secret
    debug = true

Options
=======

general
-------

secret_key
^^^^^^^^^^
This is used as the global salt for cryptographic signing throughout Inboxen.
This is sensative and should be unpredictabe. It's strongly suggested you use
at least 50 characters of numbers, both case characters and symbols from a high
entropy source.

admin_names & admin_email
^^^^^^^^^^^^^^^^^^^^^^^^^
These are a list of names and emails of the admins. Both lists must be the same
length and must be in the same order. If I were to have two admins for example,
both lists would have to be two items long::

    [general]
    admin_names = Bill, Ted
    admin_emails = bill@example.org, ted@example.org

This is used to send tracebacks when something goes wrong to the administrators.

allowed_hosts
^^^^^^^^^^^^^
This is a list of domains and/or ips that Django can serve Inboxe on. There is
support for wildcards, the syntax of which can be found in the `Django
documentation <https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts>`_.

debug
^^^^^
Enabling this puts inboxen into debug mode, this should never be used in a production
enviroment as it exposes the state of some calls in Inboxen including the settings file.
This should be used when developing on Inboxen as it allows for tracebacks to be displayed
instead of emailed and disables ``allowed_hosts`` checking.

enable_registration
^^^^^^^^^^^^^^^^^^^
A boolean flag which controls if the Inboxen instance permits registration, if disabled the
site will not allow new users to be created through the public facing site and disables the
links to the registration page.

login_attempt_cooloff
^^^^^^^^^^^^^^^^^^^^^
This is the time in minutes that the user is prevented from trying to login
after a number of failed login attempts. The value should be an integer
messured in minutes.

login_attempt_limit
^^^^^^^^^^^^^^^^^^^
This is the number of times people can attempt to login before receiving a cooldown (the
amount of time for the cooldown is dictated by ``login_attempt_cooloff``).

language_code
^^^^^^^^^^^^^
This specifies the language code that is used as a fallback when one can't be detected by
Django's locale middleware (or if the middleware is disabled). This should be set to a
standard language ID format [2]_.

static_root
^^^^^^^^^^^
This specifies where the directory is for serving static files. Django will use this
directory to place static files when using::

    python manage.py collectstatic

server_email
^^^^^^^^^^^^
The email the server uses when sending emails.

site_name
^^^^^^^^^
The name of the site.

source_link
^^^^^^^^^^^
The link to the source code for the current instance. If you change any
code in Inboxen this must be shared back under the terms of the AGPL v3,
you should populate this with the link to the source code.

time_zone
^^^^^^^^^
The timezone used for the site, this is used for example when storing dates
in the database.

Inbox
-----

inbox_length
^^^^^^^^^^^^
The number of characters of the local portion of the email so for example
in the email "pineapple@inboxen.org" the local portion is "pineapple" and
the length would be 9 characters.

min_inbox_for_request
^^^^^^^^^^^^^^^^^^^^^
This is the amount of free (unallocated) inboxes the user has before a
request to raise the limit is issued.

request_number
^^^^^^^^^^^^^^
The number amount of inboxes that the limit is increased by if a request for
more inboxes is granted.

Tasks
-----

broker_url
^^^^^^^^^^
The URL that celery will look at to find tasks and to store results.

concurrency
^^^^^^^^^^^
The number of celery processes to start

liberation
^^^^^^^^^^

path
____
Specifies the path where to temporarily store the liberation data.

database
--------

engine
^^^^^^
Which database engine to use, Django offers several database engines [3]_
however we only support:

+------------+---------------+-----------------------------+
| Database   | Engine String | Suggested Usecase           |
+============+===============+=============================+
| PostgreSQL | postgresql    | Production                  |
+------------+---------------+-----------------------------+
| SQLite     | sqlite        | Testing and Development     |
+------------+---------------+-----------------------------+

MySQL is not supported as extensive changes to Django would be required due to
the way our models work.

Oracle is not supported as it's not part of our testing. We have not ruled out
supporting it in the future.

name
^^^^
This is either the name of the database in PostgreSQL or the file name for
SQLite.

user
^^^^
User used when connecting to PostgreSQL.

This is ignored for SQLite.

password
^^^^^^^^
The password used when connecting to PostgreSQL.

This is ignored for SQLite.

host
^^^^
The host ip/address to connect to for PostgreSQL.

This is ignored for SQLite.

port
^^^^
The port to connect to for PostgreSQL.

This is ignored for SQLite.

Cache
-----

backend
^^^^^^^
This is the caching backend for inboxen, this could be one of a number of
supported backends:

+------------+-----------------------------------------+
| Backend    | Description                             |
+============+=========================================+
| database   | Uses your configured database           |
+------------+-----------------------------------------+
| file       | Uses the file system                    |
+------------+-----------------------------------------+
| memcached  | Uses Memcache                           |
+------------+-----------------------------------------+

N.B: You will need to install "pylibmc" if you want to use the ``memcached``
     backend.

timeout
^^^^^^^
The number of seconds before a cache entry is considered stale.

location
^^^^^^^^
This is either the host and port for the ``memcached`` backend or the path of
the cache directory.

.. [0] https://docs.djangoproject.com/en/1.8/ref/settings/#secret-key
.. [1] https://docs.djangoproject.com/en/1.8/topics/settings/#envvar-DJANGO_SETTINGS_MODULE
.. [2] https://docs.djangoproject.com/en/1.8/topics/i18n/#term-language-code
.. [3] https://docs.djangoproject.com/en/1.8/ref/settings/#engine
