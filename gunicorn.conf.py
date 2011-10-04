import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

# Figure out way to dynamically get virtualenv
sys.path.append("/home/chris/.virtualenvs/s2/lib/python2.6/site-packages")
sys.path.append("/home/chris/www")


bind = "127.0.0.1:29001"
logfile = "/home/chris/www/s2/logs/gunicorn.log"
workers = 3
