from django.db import models


class NewsSource(models.Model):
    """
    Probably a blog.
    """    

    name = models.CharField(max_length=1023)
    url = models.CharField(max_length=1023) 
    feed_url = models.CharField(max_length=1023) 


    def __unicode__(self):
        return self.name
