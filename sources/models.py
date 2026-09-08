from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


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


    @property
    def slug(self):
        """
        Derived rather than stored: source names are unique across all 178 of
        them and so are their slugs, and a stored slug would be one more thing
        a rebuild has to get right.

        Ninety-one of those names are domains, and slugify drops a period
        rather than breaking on it -- newspaperarchivecom. Split there first.
        """
        return slugify(self.name.replace('.', ' '))


    def get_absolute_url(self):
        return reverse('source_detail', args=[self.slug])


    class Meta:
        ordering = ('name',)


    def __str__(self):
        return self.name

class SourceUrl(models.Model):
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    url = models.CharField(max_length=1023)


# Need to make this a many-to-many
#class SourceGame(models.Model):

