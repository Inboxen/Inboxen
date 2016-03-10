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

from subprocess import Popen, PIPE
import datetime
import os

from django.contrib.messages import constants as message_constants
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from kombu.common import Broadcast, Exchange, Queue
import djcelery

from inboxen.config import *  # noqa

djcelery.setup_loader()

# Hash used to store uniqueness of certain models
# if you change this, you'll need to do a datamigration to change the rest
COLUMN_HASHER = "sha1"

##
# To override the following settings, create a separate settings module.
# Import this module, override what you need to and set the environment
# variable DJANGO_SETTINGS_MODULE to your module. See Django docs for details
##

ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = DEBUG

if not DEBUG:
    # These security settings are annoying while debugging
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

##
# Celery options
##

# load custom kombu encoder
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_RESULT_BACKEND = BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Broadcast('broadcast_tasks'),
)
CELERY_ROUTES = {'inboxen.tasks.force_garbage_collection': {'queue': 'broadcast_tasks'}}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

CELERYBEAT_SCHEDULE = {
    'statistics': {
        'task': 'inboxen.tasks.statistics',
        'schedule': datetime.timedelta(days=1),
    },
    'cleanup': {
        'task': 'inboxen.tasks.clean_orphan_models',
        'schedule': datetime.timedelta(days=1),
    },
    'requests': {
        'task': 'inboxen.tasks.requests',
        'schedule': datetime.timedelta(days=1),
    },
}

##
# Django options
##

MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

TWO_FACTOR_PATCH_ADMIN = False

LOCALE_PATHS = ["inboxen/locale"]

LANGUAGES = (
    ("en-gb", _("English")),
    ("sv-se", _("Swedish")),
)

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    ("thirdparty", os.path.join(BASE_DIR, "node_modules")),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder',
)

STATICFILES_STORAGE = 'inboxen.storage.InboxenStaticFilesStorage'

SECURE_CONTENT_TYPE_NOSNIFF = True

AUTHENTICATION_BACKENDS = (
    'inboxen.backends.RateLimitWithSettings',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.core.context_processors.request",
            "session_csrf.context_processor",
            "django.contrib.messages.context_processors.messages",
            "inboxen.context_processors.reduced_settings_context"
        ],
        'loaders': [
            # Make sure all custom template tags are thread safe
            # https://docs.djangoproject.com/en/1.6/howto/custom-template-tags/#template-tag-thread-safety
            ('django.template.loaders.cached.Loader', (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )),
        ],
        'debug': DEBUG,
    },
}]

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'inboxen.middleware.RateLimitMiddleware',
    'inboxen.middleware.ExtendSessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # third party
    'bootstrapform',
    'django_assets',
    'django_extensions',
    'djcelery',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'watson',

    # Inboxen
    'inboxen',
    'account',
    'blog',
    'liberation',
    'redirect',
    'router',
    'source',
    'termsofservice',
    'tickets',
)

SILENCED_SYSTEM_CHECKS = [
    "security.W003",  # we're using a 3rd party csrf package
    "security.W004",  # HSTS should be done via the HTTPd
    "security.W007",  # doesn't affect Firefox and Chrome?
]

ROOT_URLCONF = 'inboxen.urls'

LOGIN_URL = urlresolvers.reverse_lazy("user-login")
LOGOUT_URL = urlresolvers.reverse_lazy("user-logout")
LOGIN_REDIRECT_URL = urlresolvers.reverse_lazy("user-home")


LOGOUT_MSG = _("You are now logged out. Have a nice day!")

X_FRAME_OPTIONS = "DENY"

# CSP settings
CSP_REPORT_ONLY = False
CSP_REPORT_URI = urlresolvers.reverse_lazy("csp_logger")

if DEBUG:
    # local dev made easy
    INSTALLED_APPS += ('debug_toolbar',)
    CSP_REPORT_ONLY = True

# csrf
ANON_ALWAYS = True
CSRF_FAILURE_VIEW = "inboxen.views.error.permission_denied"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'inboxen.wsgi.application'

##
# Salmon. Splash.
##

SALMON_SERVER = {"host": "localhost", "port": 8823, "type": "smtp"}

##
# Misc.
##

try:
    process = Popen("git rev-parse HEAD".split(), stdout=PIPE, close_fds=True, cwd=BASE_DIR)
    output = process.communicate()[0].strip()
    if not process.returncode:
        os.environ["INBOXEN_COMMIT_ID"] = output
    else:
        os.environ["INBOXEN_COMMIT_ID"] = "UNKNOWN"
except OSError, TypeError:
    os.environ["INBOXEN_COMMIT_ID"] = "UNKNOWN"


## LOGGING
if DEBUG:
    log_level = "INFO"
else:
    log_level = "WARNING"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': log_level,
        },
        'inboxen': {
            'handlers': ['console'],
            'level': log_level,
        },
        'account': {
            'handlers': ['console'],
            'level': log_level,
        },
        'blog': {
            'handlers': ['console'],
            'level': log_level,
        },
        'liberation': {
            'handlers': ['console'],
            'level': log_level,
        },
        'redirect': {
            'handlers': ['console'],
            'level': log_level,
        },
        'router': {
            'handlers': ['console'],
            'level': log_level,
        },
        'source': {
            'handlers': ['console'],
            'level': log_level,
        },
        'termsofservice': {
            'handlers': ['console'],
            'level': log_level,
        },
        'tickets': {
            'handlers': ['console'],
            'level': log_level,
        },
    },
}
