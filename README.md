infrastructure
==============

A place to discuss issues that affect both the front- and back-end

Also, a repo to make the whole thing easier to deploy :)`

website, router, and queue are submodules, they all expect to find the inboxen
package in PATH

See also: https://etherpad.mozilla.org/inboxen

settings.py
-----------

You need to set LIBERATION_PATH (full path to where archives of liberated email
will be kept), LIBERATION_SUBJECT (subject line of the email sent to users) and
LIBERATION_BODY (the body of the same email)
