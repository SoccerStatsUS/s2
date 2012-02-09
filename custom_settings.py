
DEBUG = True

if DEBUG:
    PROJECT_DIR = "/home/chris/www/sdev/"
    DB_PATH = '/home/chris/www/sdev/db/soccer.db'
    CACHE_MIDDLEWARE_KEY_PREFIX = "dev:"
    CACHES = {}


else:
    PROJECT_DIR = "/home/chris/www/s2/"
    DB_PATH = '/home/chris/www/s2/db/soccer.db'
