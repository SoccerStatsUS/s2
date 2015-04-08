from django.db import models

from sources.models import Source

# Going to have to figure out how to save these while rebuilding the database.
# Probably keep a separate database for persistent / non-built data.


class NewsSource(models.Model):
    """
    Probably a blog.
    """    
    # Use djangoproject.com's feed aggregator to build this.
    #? http://github.com/miracle2k/feedplatform 
    # http://birdhouse.org/blog/2009/10/20/generating-rss-mashups-from-django/


    name = models.CharField(max_length=1023)
    url = models.CharField(max_length=1023) 
    feed_url = models.CharField(max_length=1023) 

    # tags = models.ManyToManyField?



    def __str__(self):
        return self.name

    class Meta:
        pass




class FeedItem(models.Model):
    """
    A single rss item.
    """

    title = models.CharField(max_length=1023)
    dt = models.DateTimeField()
    summary = models.CharField(max_length=1023) 
    url = models.CharField(max_length=1023) 
    source = models.ForeignKey(Source)

    def time(self):
        return self.dt.strftime("%I:%M %p")

    class Meta:
        pass
