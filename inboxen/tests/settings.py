from __future__ import absolute_import
import os

os.environ['INBOX_TESTING'] = '1'
from inboxen.settings import *

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
    }
}

db = os.environ.get('DB', "sqlite")
postgres_user = os.environ.get('PG_USER', 'postgres')

SECRET_KEY = "This is a test, you don't need secrets"
ENABLE_REGISTRATION = True
SECURE_SSL_REDIRECT = False

if db == "sqlite":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }
elif db == "postgres":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'inboxen',
            'USER': postgres_user,
        },
    }
else:
    raise NotImplementedError("Please check tests/settings.py for valid DB values")
