from __future__ import absolute_import
import os

os.environ['INBOXEN_TESTING'] = '1'
from inboxen.settings import *

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
    }
}

postgres_user = os.environ.get('PG_USER', 'postgres')

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
