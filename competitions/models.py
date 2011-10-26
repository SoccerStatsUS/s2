from django.db import models
from django.template.defaultfilters import slugify


from s2.bios.models import Bio


class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            return Competition.objects.create(name=name)


class Competition(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    objects = CompetitionManager()

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    def abbreviation(self):
        words = self.name.split(' ')
        first_letters = [e.strip()[0] for e in words if e.strip()]
        first_letters = [e for e in first_letters if e != '(']
        return "".join(first_letters)



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Competition, self).save(*args, **kwargs)


    def alltime_standings(self):
        from standings.models import Standing
        return Standing.objects.filter(competition=self, season=None)

    def first_alltime_standing(self):
        return self.alltime_standings()[0]






class SeasonManager(models.Manager):

    def find(self, name, competition):
        try:
            return Season.objects.get(name=name, competition=competition)
        except:
            return Season.objects.create(name=name, competition=competition)


class Season(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    competition = models.ForeignKey(Competition)


    objects = SeasonManager()


    class Meta:
        ordering = ("competition", "name")



    def __unicode__(self):
        return "%s: %s" % (self.competition, self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Season, self).save(*args, **kwargs)



    def previous_season(self):
        seasons = Season.objects.filter(competition=self.competition)
        index = list(seasons).index(self)
        if index > 0:
            return seasons[index - 1]
        else:
            return None

    def next_season(self):
        seasons = Season.objects.filter(competition=self.competition)
        index = list(seasons).index(self)
        next = index + 1
        if next < seasons.count():
            return seasons[next]
        else:
            return None


    def players(self):
        from s2.stats.models import Stat
        season_stats = Stat.objects.filter(competition=self.competition, season=self)
        return set([e[0] for e in season_stats.values_list("player_id")])


    def players_diff(self, season):
        ids = self.players() - season.players()
        return Bio.objects.filter(id__in=ids)

    def players_added(self):
        return self.players_diff(self.previous_season())

    def players_lost(self):
        return 
        
        
    def get_next_name(self):
        try:
            name = int(self.name)
            return unicode(name + 1)
        except:
            # Need to do a regular expression?
            return None

            
    def first_standing(self):
        return self.standing_set.all()[0]

