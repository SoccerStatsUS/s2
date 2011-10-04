import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'soccer.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

# Figure out way to dynamically get virtualenv
sys.path.append("/home/chris/.virtualenvs/soccer/lib/python2.6/site-packages")
sys.path.append("/home/chris/www")


bind = "127.0.0.1:29001"
logfile = "/home/chris/www/soccer/logs/gunicorn.log"
workers = 3
