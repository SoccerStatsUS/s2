from os.path import join
import socket

from secret_settings import *
from custom_settings import *

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

PRODUCTION_SITES = (
    "bert",
)


TEMPLATE_CONTEXT_PROCESSORS += (
    'bios.context_processors.debug_mode',
)    



INTERNAL_IPS = ('127.0.0.1',)


TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ("Chris Edgemon", 'chris@socceroutsider.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'django_db',                      # Or path to database file if using sqlite3.
        'USER': 'django',                      # Not used with sqlite3.
        'PASSWORD': 'dolly',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_PATH,
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Fix this soon.
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/home/chris/www/s2/run/messages' # change this to a proper location
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'chris@socceroutsider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True




# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True



MEDIA_ROOT = '%s/media' % PROJECT_DIR

# Make sure to use a trailing slash for these.
MEDIA_URL = "http://media.socceroutsider.com/"
ADMIN_MEDIA_PREFIX = 'http://media.socceroutsider.com/admin/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',


)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    "%s/templates" % PROJECT_DIR,
)

FIXTURE_DIR = "%s/fixtures" % PROJECT_DIR,

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'gunicorn',
    'debug_toolbar',

    'awards',
    'bios',
    'competitions',
    'contact',
    'dates',
    'drafts',
    'games',
    'goals',
    'lineups',
    'places',
    'positions',
    'sources',
    'standings',
    'stats',
    'teams',

    'haystack',
    'django_extensions',
)

# Various apps available
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = '%s/run/search' % PROJECT_DIR


