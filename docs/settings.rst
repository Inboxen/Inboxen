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

The settings file is required to set basic option for your Inboxen instance.
It contains some secret information such as the ``secret_key``, you should
ensure the permissions are set correctly and also that this file is kept safe
as without it sessions, cookie storage and along with other things rely on this
will not work [0]_.

The Inboxen settings file can be located in several places on a system, it will
use the first one it finds. Inboxen looks for the files in this order:

1. The path specified in the environment variable: ``INBOXEN_CONFIG``
2. ~/.config/inboxen/inboxen.config
3. inboxen.config in the current working directory
4. inboxen.config inside the base directory of the Inboxen project

If you're familiar with Django and would like to use your own settings module,
you can set ``DJANGO_SETTINGS_MODULE`` in the usual way [1]_.

Example configuration
=====================

This also contains the default values for all configuration values.

.. literalinclude:: ../inboxen/config_defaults.yaml
    :language: yaml

Minimum Development Configuration
=================================

To hit the ground running, the minimum you need to setup a development instance
is:

.. code-block:: yaml

    secret_key: something-secret
    debug: true

Options
=======

secret_key
----------
This is used as the global salt for cryptographic signing throughout Inboxen.
This is security sensitive and should be generated using a random number
generator. It's strongly suggested you use at least 50 characters of numbers,
both case characters and symbols from a high entropy source.

admins
------

This should be pairs of values denoting the name and email address of your admins, like so:

.. code-block:: yaml

    admins:
      - - Me
        - me@example.com
      - - You
        - you@example.com

allowed_hosts
-------------

This is a list of domains and/or IPs that Django will serve Inboxen on. There is
support for wildcards, the syntax of which can be found in the `Django
documentation <https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts>`_.

site_url
--------

This value is prefixed to all URLs that are used in contexts outside of webpages, i.e. admin email notifications

debug
-----

Enabling this puts Inboxen into debug mode, this should never be used in a production
environment as it exposes the state of some calls in Inboxen including the settings file.
This should be used when developing on Inboxen as it allows for tracebacks to be displayed
instead of emailed and disables ``allowed_hosts`` checking.

enable_registration
-------------------

A boolean flag which controls if the Inboxen instance permits registration, if disabled the
site will not allow new users to be created through the public facing site and disables the
links to the registration page.

language_code
-------------

This specifies the language code that is used as a fallback when one can't be detected by
Django's locale middleware (or if the middleware is disabled). This should be set to a
standard language ID format [2]_.

static_root
-----------

This specifies where the directory is for serving static files. Django will use this
directory to place static files when using::

    python manage.py collectstatic

meida_root
-----------

This specifies where the directory is for uploading media via the CMS. It should
be writable by the Django app.

server_email
------------

The email the server uses when sending emails.

site_name
---------

The name of the site as displayed in page titles.

source_link
-----------

The link to the source code for the current instance. If you change any
code in Inboxen this must be shared back under the terms of the AGPL v3,
you should populate this with the link to the source code.

issue_link
----------

The link to the issue tracker. This link is displayed on error pages to
encourage users to report problems.

time_zone
---------

The timezone used for the site, this is used for example when storing dates
in the database.

per_user_email_quota
--------------------

If not ``0``, this is the maximum number of emails a user can have before they
need to delete some. This deletion can be done automatically if the user
prefers.

ratelimits
----------

Rate limits control various parts of Inboxen. Each rate limit section has a
window (the timeframe a rate limit should be considering) and a count (the
maximum number of times whatever that rate limit is protecting can happen with
a window).

The following rate limits are available:

inbox
^^^^^

Controls how often a single user can create an inbox. Useful to prevent someone
from exhausting all available inboxes.

login
^^^^^

Controls how often a user can try to login. This slows down password guessing
attempts, but can block users who genuinely can't remember their passwords.

register
^^^^^^^^

Controls how often a given IP can register a new account. Prevents
circumventing of the inbox ratelimit.

single_email
^^^^^^^^^^^^

Controls how often a user can download a single email. This is quite an intense
workload for the server, so it is ratelimited to prevent the instance becoming
overloaded.

tasks
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
Specifies the path where to store the liberation data. This needs to be kept
secure as it will contain user data.

sendfile_backend
________________

Which method should be used to accelerate liberation data downloads. This
should be a dotted path to the django_sendfile2 backend you wish to use.

database
--------

name
^^^^

The name of the database.

user
^^^^
User used when connecting to PostgreSQL.

password
^^^^^^^^
The password used when connecting to PostgreSQL.

host
^^^^
The host name or IP address to connect to for PostgreSQL.

port
^^^^
The port to connect to for PostgreSQL.

Cache
-----

backend
^^^^^^^

The dotted path of the cache module you'd like to use.

timeout
^^^^^^^

The number of seconds before a cache entry is considered stale.

location
^^^^^^^^
This is either the host and port for the ``memcached`` backend or the path of
the cache directory.

.. [0] https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
.. [1] https://docs.djangoproject.com/en/2.2/topics/settings/#envvar-DJANGO_SETTINGS_MODULE
.. [2] https://docs.djangoproject.com/en/2.2/topics/i18n/#term-language-code
