from django.db import models


class SourceManager(models.Manager):

    def source_dict(self):
        """
        Returns a dict mapping a name to a source id.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
            if e.base_url:
                d[e.base_url] = e.id

        return d



class Source(models.Model):
    """
    A source is usually a book or url.
    Or something.
    """

    name = models.CharField(max_length=1023)
    author = models.CharField(max_length=1023)
    base_url = models.CharField(max_length=1023) 

    games = models.IntegerField()
    stats = models.IntegerField()

    objects = SourceManager()


    class Meta:
        ordering = ('name',)


    def __unicode__(self):
        return self.name


# Need to make this a many-to-many
#class SourceGame(models.Model):

