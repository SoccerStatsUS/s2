from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'soccerstats_build',
        'USER': 'soccerstats',
        'PASSWORD': 'ymctas',
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}
