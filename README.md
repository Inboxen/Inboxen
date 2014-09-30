Inboxen
=======

[![Build Status](https://travis-ci.org/Inboxen/Inboxen.svg?branch=master)](https://travis-ci.org/Inboxen/Inboxen)

This is the complete system with everything you need to set up Inboxen. Please
use the "deploy" branch if you wish to use this in production - "master"
sometimes breaks!

Join us in our IRC channel! We're in the #inboxen channel on [MegNet](https://www.megworld.co.uk/irc/)

See also: <https://etherpad.mozilla.org/inboxen>

Deploying
---------

Set yourself up with a virtual environment and run the following:

```
git clone https://github.com/Inboxen/Inboxen.git
cd Inboxen
# optional step
#git checkout deploy
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

Webserver
---------

The WSGI script can be found at `website/wsgi.py`

If your WSGI daemon supports it (e.g. mod_wsgi), we provide an "import script"
to improve performance for the first request after a reload. It can be found at
`website/importscript.py`

Collecting Static Files
-----------------------

Remember to run `python manage.py collectstatic`!
