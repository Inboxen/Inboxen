##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen  If not, see <http://www.gnu.org/licenses/>.
##

from datetime import timedelta
import os

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy

from configobj import ConfigObj
from validate import Validator

import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.dirname(__file__)

config_spec = os.path.join(BASE_DIR, "inboxen/config_spec.ini")
config_path = os.path.join(BASE_DIR, "settings.ini")
db_dict = {
            "postgresql": "django.db.backends.postgresql_psycopg2",
            "mysql": "django.db.backends.mysql",
            "oracle": "django.db.backends.oracle",
            "sqlite": "django.db.backends.sqlite3"
            }
validator = Validator()

config = ConfigObj(config_path, configspec=config_spec)
config.validate(validator)

## START boxen
### general
general_conf = config["general"]
try:
    SECRET_KEY = general_conf["secret_key"]
except KeyError:
    raise ImproperlyConfigured("You must set 'secret_key' in your settings.in")

if len(general_conf["admin_names"]) != len(general_conf["admin_emails"]):
    raise ImproperlyConfigured("You must have the same number of admin_names as admin_emails settings.in")

ADMINS = zip(general_conf["admin_names"], general_conf["admin_emails"])
ALLOWED_HOSTS = general_conf["allowed_hosts"]
DEBUG = general_conf["debug"]
ENABLE_REGISTRATION = general_conf["enable_registration"]
LANGUAGE_CODE = general_conf["language_code"]
LOGIN_ATTEMPT_COOLOFF = general_conf["login_attempt_cooloff"]
LOGIN_ATTEMPT_LIMIT = general_conf["login_attempt_limit"]
SERVER_EMAIL = general_conf["server_email"]
SITE_NAME = general_conf["site_name"]
STATIC_ROOT = os.path.join(BASE_DIR, general_conf["static_root"])
TIME_ZONE = general_conf["time_zone"]

### inboxes
inbox_conf = config["inbox"]
INBOX_LENGTH = inbox_conf["inbox_length"]
MIN_INBOX_FOR_REQUEST = inbox_conf["min_inbox_for_request"]
REQUEST_NUMBER = inbox_conf["request_number"]

### task queue stuff
tasks_conf = config["tasks"]
BROKER_URL = tasks_conf["broker_url"]
CELERYD_CONCURRENCY = tasks_conf["concurrency"]
LIBERATION_BODY = tasks_conf["liberation"]["body"]
LIBERATION_PATH = os.path.join(BASE_DIR, tasks_conf["liberation"]["path"])
LIBERATION_SUBJECT = tasks_conf["liberation"]["subject"]

### db
db_conf = config["database"]
DATABASES = {
    'default': {
        'ENGINE': db_dict[db_conf["engine"]],
        'USER': db_conf["user"],
        'PASSWORD': db_conf["password"],
        'HOST': db_conf["host"],
        'PORT': db_conf["port"],
    }
}

if db_conf["engine"] == "sqlite":
    DATABASES["default"]["NAME"] = os.path.join(BASE_DIR, db_conf["name"])
else:
    DATABASES["default"]["NAME"] = db_conf["name"]

## END boxen

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


CELERY_RESULT_BACKEND = BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERYBEAT_SCHEDULE = {
    'statistics':{
        'task':'queue.tasks.statistics',
        'schedule':timedelta(hours=6),
    },
    'cleanup':{
        'task':'queue.delete.tasks.clean_orphan_models',
        'schedule':timedelta(hours=2),
    },
}

# if you change this, you'll need to do a datamigration to change the rest
COLUMN_HASHER = "sha1"

MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

TEMPLATE_DEBUG = DEBUG

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AUTHENTICATION_BACKENDS = (
    'website.backends.RateLimitWithSettings',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'inboxen_cache'),
    }
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "website.context_processors.reduced_settings_context"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'website.middleware.RateLimitMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'django_extensions',
    'djcelery',
    'inboxen',
    'website',
    'queue',
    'queue.delete',
    'queue.liberate',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

ROOT_URLCONF = 'website.urls'

LOGIN_URL = reverse_lazy("user-login")
LOGOUT_URL = reverse_lazy("user-logout")
LOGIN_REDIRECT_URL = reverse_lazy("user-home")

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'website.wsgi.application'
