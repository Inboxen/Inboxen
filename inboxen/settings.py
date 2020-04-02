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

import datetime
import os
import string

from django import urls
from django.contrib.messages import constants as message_constants
from django.utils.translation import ugettext_lazy as _
from kombu.common import Broadcast, Exchange, Queue

from inboxen.config import *  # noqa

# Hash used to store uniqueness of certain models
# if you change this, you'll need to do a datamigration to change the rest
COLUMN_HASHER = "sha1"

# passed directly to get_random_string when creating an Inbox
INBOX_CHOICES = string.ascii_lowercase

# if auto-delete has been enabled for a user, this is how many days old an
# email has to be before it will be considered for delition
INBOX_AUTO_DELETE_TIME = 30

# Pagination
INBOX_PAGE_SIZE = 25
HOME_PAGE_SIZE = 25

##
# To override the following settings, create a separate settings module.
# Import this module, override what you need to and set the environment
# variable DJANGO_SETTINGS_MODULE to your module. See Django docs for details
##

##
# Celery options
##

# load custom kombu encoder
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_RESULT_BACKEND = CELERY_BROKER_URL  # noqa: F405
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TASK_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Broadcast('broadcast_tasks'),
)
CELERY_TASK_ROUTES = {'inboxen.tasks.force_garbage_collection': {'queue': 'broadcast_tasks'}}

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

CELERY_BEAT_SCHEDULE = {
    'statistics': {
        'task': 'inboxen.tasks.statistics',
        'schedule': datetime.timedelta(days=1),
    },
    'cleanup': {
        'task': 'inboxen.tasks.clean_orphan_models',
        'schedule': datetime.timedelta(days=1),
    },
    'sessions': {
        'task': 'inboxen.tasks.clean_expired_session',
        'schedule': datetime.timedelta(days=1),
    },
    'auto-delete': {
        'task': 'inboxen.tasks.auto_delete_emails',
        'schedule': datetime.timedelta(days=1),
    },
    'quota': {
        'task': 'inboxen.tasks.calculate_quota',
        'schedule': datetime.timedelta(hours=1),
    },
    'ice': {
        'task': 'inboxen.account.tasks.user_ice',
        'schedule': datetime.timedelta(days=1),
    },
}

USER_ICE_TASKS = (
    (datetime.timedelta(days=90), datetime.timedelta(days=180), "inboxen.account.tasks.user_ice_disable_emails"),
    (datetime.timedelta(days=180), datetime.timedelta(days=360), "inboxen.account.tasks.user_ice_delete_emails"),
    (datetime.timedelta(days=360), None, "inboxen.account.tasks.user_ice_delete_user"),
)

##
# Django options
##

MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

TEST_RUNNER = 'inboxen.test.InboxenTestRunner'

TWO_FACTOR_PATCH_ADMIN = False

LANGUAGE_CODE = "en-gb"

LANGUAGES = (
    ("en-gb", "English"),
)

# required for makemessages --all to work correctly, otherwise Django looks in
# conf/locale and locale (which don't exist) for languages to process
LOCALE_PATHS = [os.path.join(BASE_DIR, "inboxen/locale")]  # noqa: F405

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
        os.path.join(os.getcwd(), "frontend", "build", "compiled"),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
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
            "django.template.context_processors.debug",
            "django.template.context_processors.i18n",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            "django.template.context_processors.request",
            "django.template.context_processors.csrf",
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
        'debug': DEBUG,  # noqa: F405
    },
}]

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'inboxen.async_messages.middleware.AsyncMiddleware',
    'inboxen.middleware.RateLimitMiddleware',
    'inboxen.middleware.ExtendSessionMiddleware',
    'inboxen.middleware.MakeXSSFilterChromeSafeMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'elevate.middleware.ElevateMiddleware',
    'csp.middleware.CSPMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',

    # Main Inboxen app
    'inboxen',

    # Other Inboxen apps
    'inboxen.account',
    'inboxen.async_messages',
    'inboxen.blog',
    'inboxen.cms',
    'inboxen.liberation',
    'inboxen.redirect',
    'inboxen.router',
    'inboxen.source',
    'inboxen.tickets',
    'inboxen.search',

    # third party
    'bootstrapform',
    'django_extensions',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'elevate',
    'two_factor',
)

ROOT_URLCONF = 'inboxen.urls'

# search
SEARCH_CONFIG = "english"
SEARCH_TIMEOUT = 60 * 30  # 30 minutes
SEARCH_PAGE_SIZE = 25

LOGIN_URL = urls.reverse_lazy("user-login")
LOGOUT_URL = urls.reverse_lazy("user-logout")
LOGIN_REDIRECT_URL = urls.reverse_lazy("user-home")

LOGOUT_MSG = _("You are now logged out. Have a nice day!")

REGISTER_LIMIT_CACHE_PREFIX = "inboxen-register-"
INBOX_LIMIT_CACHE_PREFIX = "inboxen-inbox-"
SINGLE_EMAIL_LIMIT_CACHE_PREFIX = "inboxen-single-email-"

X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSP settings
CSP_REPORT_ONLY = False
CSP_REPORT_URI = urls.reverse_lazy("csp_logger")
CSP_DEFAULT_SRC = ("'none'",)

CSP_CONNECT_SRC = ("'self'",)
CSP_FONT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_MANIFEST_SRC = ("'self'",)

CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_FAILURE_VIEW = "inboxen.views.error.csrf_failure"

ELEVATE_URL = urls.reverse_lazy("user-sudo")

CMS_ROOT_URL = urls.reverse_lazy("cms-index", args=('',))

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'inboxen.wsgi.application'

##
# Salmon. Splash.
##

SALMON_SERVER = {"host": "localhost", "port": 8823, "type": "smtp"}

##
# Misc.
##

# trailing space is important
EMAIL_SUBJECT_PREFIX = "[{}] ".format(SITE_NAME)  # noqa: F405

##
# LOGGING
##
if DEBUG:  # noqa: F405
    log_level = "INFO"
    salmon_log_level = "DEBUG"
else:
    log_level = "WARNING"
    salmon_log_level = "WARNING"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'is_not_salmon': {
            '()': 'inboxen.utils.log.IsNotSalmon',
        },
    },
    'handlers': {
        'console': {
            'level': log_level,
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'is_not_salmon'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': log_level,
        },
        'inboxen': {
            'handlers': ['console', 'mail_admins'],
            'level': log_level,
        },
        'ratelimitbackend': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


SALMON_LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': '',
        },
    },
    'handlers': {
        'file': {
            'level': salmon_log_level,
            'class': 'logging.FileHandler',
            'filename': "logs/salmon.log",
            'formatter': 'default',
        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': salmon_log_level,
        },
        'routing': {
            'handlers': ['file'],
            'level': salmon_log_level,
            'propagate': False
        },
    },
}

if DEBUG:  # noqa: F405
    # local dev made easy
    INTERNAL_IPS = ["127.0.0.1"]
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_CONFIG = {"JQUERY_URL": None}
    CSP_REPORT_ONLY = True
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
