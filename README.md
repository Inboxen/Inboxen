Inboxen - infrastructure
==============

[![Build Status](https://travis-ci.org/Inboxen/infrastructure.svg?branch=master)](https://travis-ci.org/Inboxen/infrastructure)

A place to bring together the project as a whole.

Also, a repo to make the whole thing easier to deploy :)

`website`, `router`, and `queue` are submodules, they all expect to find the `inboxen`
package in `PYTHONPATH`.

Join us in our IRC channel! We're in the #inboxen channel on [MegNet](https://www.megworld.co.uk/irc/)

See also: <https://etherpad.mozilla.org/inboxen>

Deploying
---------

Set yourself up with a virtual environment and run the following:

```
git clone https://github.com/Inboxen/infrastructure.git inboxen
cd inboxen
git submodule init
git submodule update
pip install -r requirements.txt
```

After this has completed, see the next section on minimum configuration. Also,
`settings.py` is well commented and explains what various configuration options
do.

settings.ini
-----------

At the very least, this file should contain the following:

```
[general]
secret_key = some_random_string
```

Where `some_random_string` is a long (at least a length of 50) string,
containing random characters.
