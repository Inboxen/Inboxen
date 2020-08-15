Inboxen
=======

[![Tests](https://github.com/Inboxen/Inboxen/actions/workflows/tests.yml/badge.svg)](https://github.com/Inboxen/Inboxen/actions/workflows/tests.yml)
[![Test coverage](http://codecov.io/github/Inboxen/Inboxen/coverage.svg)](http://codecov.io/github/Inboxen/Inboxen)
[![Documentation Status](https://readthedocs.org/projects/inboxen/badge/?version=latest)](https://inboxen.readthedocs.io/en/latest/?badge=latest)

This is the main codebase behind Inboxen.

The current maintainer of this repo is [Matt Molyneaux](https://github.com/moggers87)

GPG keys
--------

GPG keys used by Inboxen developers to sign releases:

```
Matt Molyneaux <moggers87@moggers87.co.uk>
    19F5 A8DC C917 FD00 E859   02F4 878B 5A2A 1D47 C084
```

Security
--------

If you find a security issue with Inboxen, email <security@moggers87.co.uk>. If
you wish to send an encrypted report, then please use key id `0x878B5A2A1D47C084`

Once reported, all security vulnerabilities will be acted on immediately and a
fix with full disclosure will go out to everyone at the same time.

Developing
----------

You'll need the following tools:

* Git
* Python (we strongly recommend you use virtualenv too)
* PostgreSQL
* NodeJS
* GNU Make
* [EditorConfig](http://editorconfig.org/) *(optional)*

This project comes with a `.editorconfig` file - we recommend installing it to
avoid things like mixing tabs/spaces or accidentally saving files with
DOS-style newlines.

Set yourself up with a virtual environment and run the following:

```
git clone https://github.com/Inboxen/Inboxen.git
cd Inboxen
make
```

When you've made your changes, remember to check your code
style and run unit tests.

Python tests:

```
python manage.py test
```

JS tests:

```
npx grunt karma
```

To check code style on Python:

```
tox -e isort,lint
```

And finally, check JS code style:

```
npx grunt jshint
```

### Local HTTP server

You'll need a `inboxen.config` file, for example:

```
secret_key: some_random_string
debug: true
tasks:
  always_eager: true
```

If you want to start a local HTTP server to test out your changes, run the following:

```
python manage.py runserver
```

You can connect to it on <http://localhost:8000/>.

With `debug=true`, you'll have the Django Debug Toolbar enabled and you can
find the Inboxen styleguide at <http://localhost:8000/styleguide>

Committing and Branching
------------------------

### Branching

All development happens in branches off of `main`. Each branch should have an
associated issue - if there isn't one for what you're working on then create a
new issue first!

Branch names should be of the format `<issue>-<description>` where:

* `<issue>` is the issue you are working on
* `<description>` is a brief description of what's happening on that branch

For example, `129-pin-inboxes` was the branch used for implementing the [pin
inbox feature](https://github.com/Inboxen/Inboxen/issues/129)

Finished branches are then merged into `main`. If there is someone available
to review your branch, your branch should be reviewed and merged by them.
Remember to add a note to CHANGELOG.md when merging!

#### Hotfix branches

Hotfixes should be branched from the latest deploy tag, and then be tagged
themselves as a normal deployment before being merged back into `main`.

### Commit messages

You should follow the pattern of "summary, gap, details, gap, issue references"

For example:

```
Blah blah thing

Fixes this thing, changes how we should do something else

fix #345
touch #234
```

If you are committing on `main`, then make sure to end your commit message
with "IN MAIN" so we know who to blame when stuff breaks.
