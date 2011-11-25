from django.db import models



class Source(object):

    name = models.CharField(max_length=1023)


