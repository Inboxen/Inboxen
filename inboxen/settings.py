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
import stat
import warnings

from django.contrib.messages import constants as message_constants
from django.core import exceptions, urlresolvers
from django.utils.translation import ugettext_lazy as _

from kombu.common import Broadcast, Exchange, Queue
import configobj
import djcelery
import validate

djcelery.setup_loader()

##
# Most configuration can be done via settings.ini
#
# The file is searched for in the follow way:
# 1. The environment variable "INBOXEN_CONFIG", which contains an absolute path
# 2. ~/.config/inboxen/settings.ini
# 3. settings.ini in the root of the git repo (i.e. the same directory as "manage.py")
#
# See inboxen/config_spec.ini for defaults, see below for comments
##

# Shorthand for Django's default database backends
db_dict = {
    "postgresql": "django.db.backends.postgresql_psycopg2",
    "mysql": "django.db.backends.mysql",
    "oracle": "django.db.backends.oracle",
    "sqlite": "django.db.backends.sqlite3",
    }

# Shorthand for Django's default database backends
cache_dict = {
    "database": "django.core.cache.backends.db.DatabaseCache",
    "dummy": "django.core.cache.backends.dummy.DummyCache",
    "file": "django.core.cache.backends.filebased.FileBasedCache",
    "localmem": "django.core.cache.backends.locmem.LocMemCache",
    "memcached": "django.core.cache.backends.memcached.PyLibMCCache",
    }

is_testing = bool(int(os.getenv('INBOX_TESTING', '0')))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if os.path.exists(os.getenv('INBOX_CONFIG', '')):
    CONFIG_PATH = os.getenv('INBOX_CONFIG')
elif os.path.exists(os.path.expanduser("~/.config/inboxen/settings.ini")):
    CONFIG_PATH = os.path.expanduser("~/.config/inboxen/settings.ini")
elif os.path.exists(os.path.join(BASE_DIR, "settings.ini")):
    CONFIG_PATH = os.path.join(BASE_DIR, "settings.ini")
elif is_testing:
    CONFIG_PATH = ""
else:
    raise exceptions.ImproperlyConfigured("You must provide a settings.ini file")

# Check that our chosen settings file cannot be interacted with by other users
try:
    mode = os.stat(CONFIG_PATH).st_mode
except OSError:
    warnings.warn("Couldn't find settings.ini", ImportWarning)
else:
    if mode & stat.S_IRWXO != 0:
        warnings.warn("Other users could be able to interact with your settings file. Please check file permissions on %s" % CONFIG_PATH)

config_spec = os.path.join(BASE_DIR, "inboxen/config_spec.ini")

config = configobj.ConfigObj(CONFIG_PATH, configspec=config_spec)
config.validate(validate.Validator())

# TODO: These could be merged into a custom validator
try:
    SECRET_KEY = config["general"]["secret_key"]
except KeyError:
    if is_testing:
        warnings.warn("You haven't set 'secret_key' in your settings.ini", ImportWarning)
    else:
        raise exceptions.ImproperlyConfigured("You must set 'secret_key' in your settings.ini")

if len(config["general"]["admin_names"]) != len(config["general"]["admin_emails"]):
    raise exceptions.ImproperlyConfigured("You must have the same number of admin_names as admin_emails settings.ini")

# Admins (and managers)
ADMINS = zip(config["general"]["admin_names"], config["general"]["admin_emails"])

# List of hosts allowed
ALLOWED_HOSTS = config["general"]["allowed_hosts"]

# Enable debugging - DO NOT USE IN PRODUCTION
DEBUG = config["general"]["debug"]

# Alloew new users to register
ENABLE_REGISTRATION = config["general"]["enable_registration"]

# Cooloff time, in minutes, for failed logins
LOGIN_ATTEMPT_COOLOFF = config["general"]["login_attempt_cooloff"]

# Maximum number of unsuccessful login attempts
LOGIN_ATTEMPT_LIMIT = config["general"]["login_attempt_limit"]

# Language code, e.g. en-gb
LANGUAGE_CODE = config["general"]["language_code"]

# Where `manage.py collectstatic` puts static files
STATIC_ROOT = os.path.join(BASE_DIR, config["general"]["static_root"])

# Email the server uses when sending emails
SERVER_EMAIL = config["general"]["server_email"]

# Site name used in page titles
SITE_NAME = config["general"]["site_name"]

# Link to source code
SOURCE_LINK = config["general"]["source_link"]

# Time zone
TIME_ZONE = config["general"]["time_zone"]

# Length of the local part (bit before the @) of autogenerated inbox addresses
INBOX_LENGTH = config["inbox"]["inbox_length"]

# Maximum number of free inboxes before a request for more will be generated
MIN_INBOX_FOR_REQUEST = config["inbox"]["min_inbox_for_request"]

# Increase the pool amount by this number when a user request is granted
REQUEST_NUMBER = config["inbox"]["request_number"]

# Where Celery looks for new tasks and stores results
BROKER_URL = config["tasks"]["broker_url"]

# Number of Celery processes to start
CELERYD_CONCURRENCY = config["tasks"]["concurrency"]

# Runs tasks synchronously
CELERY_ALWAYS_EAGER = config["tasks"]["always_eager"]

# Path where liberation data is temporarily stored
LIBERATION_PATH = os.path.join(BASE_DIR, config["tasks"]["liberation"]["path"])


# Databases!
DATABASES = {
    'default': {
        'ENGINE': db_dict[config["database"]["engine"]],
        'USER': config["database"]["user"],
        'PASSWORD': config["database"]["password"],
        'HOST': config["database"]["host"],
        'PORT': config["database"]["port"],
    }
}

# "name" is a path for sqlite databases
if config["database"]["engine"] == "sqlite":
    DATABASES["default"]["NAME"] = os.path.join(BASE_DIR, config["database"]["name"])
else:
    DATABASES["default"]["NAME"] = config["database"]["name"]

# Caches!
CACHES = {
    'default': {
        'BACKEND': cache_dict[config["cache"]["backend"]],
        'TIMEOUT': config["cache"]["timeout"],
    }
}

if config["cache"]["backend"] == "file":
    if config["cache"]["location"] == "":
        # sane default for minimum configuration
        CACHES["default"]["LOCATION"] = os.path.join(BASE_DIR, "inboxen_cache")
    else:
        CACHES["default"]["LOCATION"] = os.path.join(BASE_DIR, config["cache"]["location"])
else:
    CACHES["default"]["LOCATION"] = config["cache"]["location"]

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

TEMPLATE_DEBUG = DEBUG

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

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder',
)

STATICFILES_STORAGE = 'inboxen.storage.InboxenStaticFilesStorage'

AUTHENTICATION_BACKENDS = (
    'inboxen.backends.RateLimitWithSettings',
)

# Make sure all custom template tags are thread safe
# https://docs.djangoproject.com/en/1.6/howto/custom-template-tags/#template-tag-thread-safety
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "session_csrf.context_processor",
    "django.contrib.messages.context_processors.messages",
    "inboxen.context_processors.reduced_settings_context"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'inboxen.middleware.RateLimitMiddleware',
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

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

ROOT_URLCONF = 'inboxen.urls'

LOGIN_URL = urlresolvers.reverse_lazy("user-login")
LOGOUT_URL = urlresolvers.reverse_lazy("user-logout")
LOGIN_REDIRECT_URL = urlresolvers.reverse_lazy("user-home")

# CSP settings
CSP_REPORT_ONLY = True
CSP_REPORT_URI = urlresolvers.reverse_lazy("csp_logger")

# csrf
ANON_AS_LOGGED_IN = True
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
