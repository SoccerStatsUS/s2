import os
import sys

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
application = get_wsgi_application()

from settings import PROJECT_DIR

# Figure out way to dynamically get virtualenv
sys.path.append("/home/chris/.virtualenvs/s2/lib/python2.6/site-packages")
sys.path.append("/home/chris/www")


bind = "127.0.0.1:29001"
logfile = "%s/logs/gunicorn.log" % PROJECT_DIR
workers = 3
