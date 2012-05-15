from django.db import models



class Source(object):
    """
    A source is usually a book or url.
    Or something.
    """

    name = models.CharField(max_length=1023)
    url = models.CharField(max_length=1023) 


