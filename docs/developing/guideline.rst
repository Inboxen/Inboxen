.. index::
    single: Developer guidelines 

Developer Guidelines
====================

Stylistic Guideline
-------------------

We generally follow PEP-8_, with a few quirks. 

For indentation, we use four (4) spaces. If you use Vim, just stick these in
your .vimrc::

    set tabstop=4
    set shiftwidth=4
    set expandtab

Blocks of comments should begin with two hashes and end with two hashes e.g::

    ##
    # This is a block of comments.
    # 
    # It's a very good example.
    ##

Space out imports grouped by package (e.g. Django), standard library first,
Inboxen libraries last e.g::

    import sys
    import os

    from django.core import exceptions
    from django.shortcuts import render

    from pytz import utc

    from inboxen.models import Email


Git and Issue Tracking
----------------------

We're very eager for others to get involved. Even if you don't code, bug
reports and feature requests are always welcome. All our development happens
on GitHub_, including issue tracking and pull requests.

Basic things to consider for pull requests:

- Try and work on one feature per branch
- Try to separate changes into logical commits
- If there's not an issue open for what you want to work on, create one and
  link to your branch.
- You can reference issues from commit messages, `see GitHub help`_. This will
  save you from having to update the issue you're working on manually.

Smaller changes can be submitted via generating a patch with with::

    git diff

Please quote the patch using three backticks ("`") so GitHub's formatting
doesn't interfere.

**Keeping issues up to date**

Please help keep issues up to date. That doesn't just mean keeping your own
issues up to date (if you get stuck or no longer have time to work on that
issue), but also asking for a status update on other issues

.. _GitHub: https://github.com/Inboxen
.. _see GitHub help: https://help.github.com/articles/closing-issues-via-commit-messages
.. _PEP-8: http://www.python.org/dev/peps/pep-0008/
