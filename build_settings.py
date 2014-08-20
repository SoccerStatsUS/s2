from settings import *


DATABASES = {
    'default': {
        #'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'soccerstats_build',
        'USER': 'soccerstats',
        'PASSWORD': 'ymctas',
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}
