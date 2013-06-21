Developer Guideliens
====================

Stylistic Guideline
-------------------

We mostly conform to PEP-8_, it is important that the code style is kept to the same standard. We mainly use vim on the dev team, by no means you have to but if you do the settings to get 4 space tabs which we use is::

    set tabstop=4
    set shiftwidth=4
    set expandtab

A few things we should note, blocks of comments should begin with two hashes and end with two hashes e.g::

    ##
    # This is a block of comments
    # as you can see, at the top
    # we have two hashes and the rest
    # of the line is black. We then
    # have a double hash and blank line
    # at the end.
    ##

This confroms to PEP-8 but some additional considerations when using imports, if you import multiple items from a module (e.g. django) those go in their own block e.g::

    import sys
    import os

    from django.core import exceptions
    from django.shortcuts import render

    from pytz import utc

    from inboxen.models import Email

As you can see the two django imports are in their own block.


Issue Usage
-----------

We use issues quite a lot throughout Inboxen. We like to think of them as documentation throughout the development of the feature or bug fix, they are important since they allow other developers to see what is happening, it allows other developers to see potential problems you might not have thought about or suggest ideas. They also help other developers pick up development if for whatever reason you have to leave it. Follow these guidelines when using tickets:

- Claim the ticket (github offers a "owned by" on the ticket)
- If you're working on your own fork, link your issue in the issue on the main branch.
- When commiting use #<issue number>
- Post on the issue when you have a problem (even if you know the solution), it helps document it.


Git
---

We use git a lot, if you wish to commit code back (which we hope you do). Basic things to consider:

- Work on a branches when developing new features
- Try to separate out code into multiple logical commits


.. _PEP-8: http://www.python.org/dev/peps/pep-0008/
