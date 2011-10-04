import os
import sys

sys.path.append("/home/chris/.virtualenvs/soccer/lib/python2.5/site-packages")
sys.path.append("/home/chris/www")

os.environ['DJANGO_SETTINGS_MODULE'] = 'soccer.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

