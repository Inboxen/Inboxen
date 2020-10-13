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
but we find that preferable to masses of documentation of unknown quality.

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
- GCC
- GNU Make
- PostgreSQL

  - ``pg_config`` needs to be in your ``$PATH``

Setup
=====

Let's get started!


.. code-block:: shell

   $ git clone https://github.com/Inboxen/Inboxen.git
   $ cd Inboxen
   $ virtualenv-3 env
   $ . env/bin/activate
   (env) $ make
   (env) $ touch inboxen.config

At this point we should add some basic configuration. Open ``inboxen.config``
with your favourite text editor and add the following:

.. code-block:: yaml

   secret_key: some_random_string

Now we've got some configuration, let's finish the setup:

.. code-block:: shell

   (env) $ ./manage.py migrate
   (env) $ make static
   (env) $ mkdir -p run logs
   (env) $ make salmon-start celery-start

Finally, there are some external services that you will need to configure:

* Your WSGI daemon needs to be configured to use your virtualenv (found in
  ``env/``) and use the script ``inboxen/wsgi.py``. You should also set your
  current working directory to same folder the contains ``setup.py`` Refer to
  your WSGI daemon's documentation for details on how to do that.
* Your webserver or your WSGI daemon (depending on your configuration) should
  serve ``/static/`` from ``static_content``.
* Your mailserver should forward mail to ``localhost:8823`` via SMTP

Additional configuration
========================

There are a number of other configuration options that you can use. See
:doc:`settings` for all available settings.

Additional Python packages
--------------------------

You can also install additional Python packages to enable certain features. For
example, let's say that we want to use Memcache as our cahce backend. Create a
file called ``local-reqs.in`` and add the following:

.. code-block:: text

   -r requirements.txt
   pylibmc

.. note::

   As well as the Memcache backend, if you're not using RabbitMQ for your task
   queue you will need to install extra package for Celery. Those packages
   should be added to ``local-reqs.in`` as well. Refer to the Celery
   documentation for details.

.. note::

    You'll have to enable Memcache in your ``inboxen.config`` file before using
    it. The same applies to using a different Celery broker.

Always pin your dependencies!

.. code-block:: shell

   (env) $ pip-compile -U --output-file local-reqs.txt local-reqs.in
   (env) $ pip-sync local-reqs.txt

make rules
----------

As you've seen already, we provide a number of make rules for common tasks. You
can add your own in ``local.mk``. For example, you might want to have a rule to
install dependencies:

.. code-block:: text

   .PHONY: install-local-deps
   install-local: install-js-deps
       pip-sync local-reqs.txt

This would allow you to run the following:

.. code-block:: shell

   (env) $ make install-local-deps

Upgrading
=========

.. code-block:: shell

   (env) $ make salmon-stop celery-setop
   (env) $ git pull

If you specified additional Python packages, then update your pinned dependencies:

.. code-block:: shell

   (env) $ pip-compile -U --output-file local-reqs.txt local-reqs.in

Otherwise, skip this step.

Install updated packages and compile various assets:

.. code-block:: shell

   (env) $ pip-sync local-reqs.txt || pip-sync requirements.txt
   (env) $ npm install
   (env) $ ./manage.py migrate
   (env) $ make static

Finally, restart services:

.. code-block:: shell

   (env) $ make salmon-start celery-start
   (env) $ touch inboxen/wsgi.py
