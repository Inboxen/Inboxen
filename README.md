infrastructure
==============

A place to bring together the project as a whole.

Also, a repo to make the whole thing easier to deploy :)`

website, router, and queue are submodules, they all expect to find the inboxen
package in PATH

See also: https://etherpad.mozilla.org/inboxen

settings.ini
-----------

At the very least, this file should contain the following:

```
[general]
secret_key = some_random_string
```

Where `some_random_string` is a long (at least a length of 50) string,
containing random characters.
