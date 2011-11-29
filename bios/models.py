from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from collections import defaultdict
import datetime



class BioManager(models.Manager):

    def bio_dict(self):
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d


    def find(self, name, create=True):
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

    awards = generic.GenericRelation('awards.AwardItem')

    objects = BioManager()


    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Bio, self).save(*args, **kwargs)


    def age(self, date=None):
        if date is None:
            date = datetime.date.today()


        if self.birthdate:
            return date - self.birthdate
        else:
            return None


    def season_stats(self):
        return self.stat_set.exclude(team=None).exclude(season=None)


    def career_stat(self):
        from s2.stats.models import Stat
        c = Stat.career_stats.filter(player=self)
        if c:
            return c[0]
        else:
            return None

    def competition_stats(self):
        from s2.stats.models import Stat
        return Stat.competition_stats.all()

        
    def __unicode__(self):
        return self.name

        
    def get_absolute_url(self):
        return reverse('person_detail', args=[self.slug])


    def calculate_standings(self):
        from s2.stats.models import Stat

        for stat in self.stat_set.all():
            if stat.wins is None:
                stat.calculate_standings()

        #for stat in self.competition_stats():
        #    if stat.wins is None:
        #        stat.calculate_standings()

        if self.career_stat() and self.career_stat().wins is None:
            self.career_stat().calculate_standings()

        team_stats = Stat.team_stats.filter(player=self)
        for stat in team_stats:
            if stat.wins is None:
                stat.calculate_standings()






