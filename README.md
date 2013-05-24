Front End
==========
This is the web interface for inboxen and all the API end points. 

Join us in our IRC channel! We're in the #inboxen channel on [MegNet](https://www.megworld.co.uk/irc/)

If you'd like to see the site https://inboxen.org
Requirements
============
These are the requiresments to run inboxen.

- Python 2.7 (not python 3.x)
- django 1.5+
- python's MySQLdb library
- markdown
- pytz
- celery

(a celery broker suggested)
- redis

Settings.py
===========
You need to ensure that certain settings are in the settings file

- LOGIN_URL
- ENABLE REGISTRATION

Add the following block:
CELERYBEAT_SCHEDULE = {
    'statistics':{
        'task':'inboxen.tasks.statistics',
        'schedule':timedelta(hours=6),
    }
}

