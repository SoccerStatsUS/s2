from os.path import join
import socket

PRODUCTION_SITES = (
    "reyna",
)


PROJECT_DIR = "/home/chris/www/s2/",


if socket.gethostname() in PRODUCTION_SITES:
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ("Chris Edgemon", 'chrisedgemon@gmail.com'),
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
        'NAME': '/home/chris/www/s2/db/soccer.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Switch to redis.
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


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



MEDIA_ROOT = '/home/chris/www/s2/media'

# Make sure to use a trailing slash for these.
MEDIA_URL = "http://media.socceroutsider.com/"
ADMIN_MEDIA_PREFIX = 'http://media.socceroutsider.com/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zvn-9ofy_sj3j55-gs7-p6+5hsuk+q@_8-iz8+-*qobwr7snw!'

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
)

ROOT_URLCONF = 's2.urls'

TEMPLATE_DIRS = (
    "/home/chris/www/s2/templates",
)

FIXTURE_DIR = "/home/chris/www/s2/fixtures",

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    's2.awards',
    's2.bios',
    's2.competitions',
    's2.dates',
    's2.drafts',
    's2.games',
    's2.goals',
    's2.lineups',
    's2.positions',
    's2.sources',
    's2.standings',
    's2.stats',
    's2.teams',
    'django.contrib.admin',
    'gunicorn',
)
