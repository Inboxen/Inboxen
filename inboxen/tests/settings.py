from __future__ import absolute_import
import os


# tell settings module to ignore normal config file
os.environ['INBOXEN_TESTING'] = '1'
from inboxen.settings import *

# build asserts if need be
ASSETS_AUTO_BUILD = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
    }
}

# default to current user
postgres_user = os.environ.get('PG_USER', os.environ.get('USER'))

SECRET_KEY = "This is a test, you don't need secrets"
ENABLE_REGISTRATION = True
SECURE_SSL_REDIRECT = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'inboxenTest',
        'USER': postgres_user,
    },
}
