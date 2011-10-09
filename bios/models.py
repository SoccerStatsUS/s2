from django.db import models
from django.template.defaultfilters import slugify

from collections import defaultdict

class BioManager(models.Manager):

    def find(self, name):
        """
        Given a team name, determine the actual team.
        """
        if name == '':
            import pdb; pdb.set_trace()
        
        bios = Bio.objects.filter(name=name)
        if bios:
            return bios[0]
        else:
            return Bio.objects.create(name=name)


    def duplicate_slugs(self):
        d = defaultdict(list)
        for e in self.get_query_set():
            d[e.slug].append(e.name)
        return [(k, v) for (k, v) in d.items() if len(v) > 1]


class Bio(models.Model):
    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=False)

    height = models.IntegerField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    birthplace = models.CharField(max_length=250, null=True, blank=True)

    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    objects = BioManager()


    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Bio, self).save(*args, **kwargs)


    def career_stat(self):
        from s2.stats.models import Stat
        c = Stat.career_stats.filter(player=self)
        if c:
            return c[0]
        else:
            return None



        
    def __unicode__(self):
        return self.name

        
        

