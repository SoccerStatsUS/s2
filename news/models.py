from django.db import models

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



    def __unicode__(self):
        return self.name

    class Meta:
        pass




class FeedItem(object):
    """
    A single rss item.
    """


    class Meta:
        pass
