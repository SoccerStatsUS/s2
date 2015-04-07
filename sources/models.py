from django.db import models


class SourceManager(models.Manager):

    def source_dict(self):
        """
        Returns a dict mapping a name to a source id.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
            for su in e.sourceurl_set.all():
                d[su.url] = e.id

        return d



class Source(models.Model):
    """
    A source is usually a book or url.
    Or something.
    """

    name = models.CharField(max_length=1023)
    author = models.CharField(max_length=1023)
    #base_url = models.CharField(max_length=1023) 

    # Secondary data.
    games = models.IntegerField(null=True)
    stats = models.IntegerField(null=True)
    total = models.IntegerField(null=True)

    objects = SourceManager()


    class Meta:
        ordering = ('name',)


    def __unicode__(self):
        return self.name

class SourceUrl(models.Model):
    
    source = models.ForeignKey(Source)
    url = models.CharField(max_length=1023)


# Need to make this a many-to-many
#class SourceGame(models.Model):

