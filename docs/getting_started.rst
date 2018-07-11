..  Copyright (C) 2018 Jessica Tallon & Matt Molyneaux

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

===============
Getting Started
===============

There are too many options and too much difference between various
distributions (e.g. Fedora, Debian, any one of the BSDs) for us to docment from
start to finish how to deploy Inboxen for a majority for people wishing to
deploy this software for themselves. We have often been frustrated by projects
for listing Debian package names when I'm using Fedora, or listing outdated
package names entirely. As such, you're expected to be familiar with the
following:

* A webserver and deploying WSGI applications to that server.
* A mail-server and forwarding mail to another server.
* Setting up a message queue with either RabbitMQ or Redis.
* Managing a cache like Memcache.

We understand that this will make deploying Inboxen a far more daunting task,
but we find that preferable to frustrated users in our issue tracker.

.. warning:

   While Inboxen is good enough for ordinary users to navigate, admin support
   isn't so well polished. Certain admin tasks still require knowledge of
   things like Django, Celery, and Salmon

Requirements
============

To use Inboxen, you'll need the following:

- Python 3, including the following:

  - Development headers (usually in a package called ``python3-devel`` or
    ``python-dev``. If you installed via ``brew`` or from source, these headers
    will already be there.
  - ``pip``
  - ``virtualenv``

- Git
- NodeJS and ``npm``
- Ruby Sass
- GCC
- PostgreSQL

  - ``pg_config`` needs to be in your ``$PATH``

Setup
=====

Let's get started!


.. codeblock:: shell

   $ git clone https://github.com/Inboxen/Inboxen.git
   $ cd Inboxen
   $ virtualenv-3 env
   $ . env/bin/activate
   (env) $ pip install -r requirements.txt
   (env) $ npm install
   (env) $ touch settings.ini

At this point we should add some basic configuration. Open ``settings.ini``
with your favourite text editor and add the following:

.. codeblock:: ini

   [general]
   # some_random_string should be replaced by an actual random string, it is
   used for various cryptographic functions and should be kept secret
   secret_key = some_random_string

Now we've got some configuration, let's finish the setup:

.. codeblock:: shell

   (env) $ ./manage.py migrate
   (env) $ ./manage.py compilemessages
   (env) $ ./manage.py collectstatic
   (env) $ ./manage.py router --start
   (env) $ DJANGO_SETTINGS_MODULE=inboxen.settings celery -A inboxen worker -B -E -D -l info --logfile logs/celery.log --pidfile run/tasks.pid

Finally, there are some external services that you will need to configure:

* Your WSGI daemon needs to be configured to use your virtualenv (found in
  ``env/``) and use the script ``inboxen/wsgi.py``
* Your webserver should serve ``/static/`` from ``static_content``
* Your mailserver should forward mail to ``localhost:8823`` via SMTP

Upgrading
=========

.. codeblock:: shell

   (env) $ ./manage.py router --stop
   (env) $ pkill celery
   (env) $ git pull
   (env) $ pip-sync requirements.txt
   (env) $ npm install
   (env) $ ./manage.py migrate
   (env) $ ./manage.py compilemessages
   (env) $ ./manage.py collectstatic
   (env) $ ./manage.py router --start
   (env) $ DJANGO_SETTINGS_MODULE=inboxen.settings celery -A inboxen worker -B -E -D -l info --logfile logs/celery.log --pidfile run/tasks.pid
   (env) $ touch inboxen/wsgi.py
