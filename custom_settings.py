
import os

DEBUG = True

# Make sure to use a trailing slash for MEDIA_URL

if os.path.exists("Users"):
    PROJECT_ROOT = "/Users/chrisedgemon"
    PROJECT_DIRNAME = 's2'
elif DEBUG:
    PROJECT_ROOT = "/home/chris"
    PROJECT_DIRNAME = 'sdev'
else:
    PROJECT_ROOT = "/home/chris"
    PROJECT_DIRNAME = 's2'

if DEBUG:
    CACHE_MIDDLEWARE_KEY_PREFIX = "dev:"
    CACHES = {}


PROJECT_DIR = "%s/www/%s" % (PROJECT_ROOT, PROJECT_DIRNAME)
DB_PATH = "%s/www/%s/db/soccer.db" % (PROJECT_ROOT, PROJECT_DIRNAME)
