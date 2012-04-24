from django.db import models
from django.template.defaultfilters import slugify

from bios.models import Bio


class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            return Competition.objects.create(name=name)


    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d




class Competition(models.Model):
    """
    A generic competition such as MLS Cup Playoffs, US Open Cup, or Friendly
    """
    # Should this be called Tournament? Probably not.

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #international = models.BooleanField()

    objects = CompetitionManager()

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    def abbreviation(self):
        words = self.name.split(' ')
        first_letters = [e.strip()[0] for e in words if e.strip()]
        first_letters = [e for e in first_letters if e not in '-()']
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

    def first_season(self):
        return self.season_set.all()[0]

    def last_season(self):
        seasons = self.season_set.count()
        index = seasons - 1
        return self.season_set.all()[index]






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


    def dates(self):
        try:
            year = int(self.name)
            start = datetime.datetime(year, 1, 1)
            end = datetime.datetime(year + 1, 12, 31)
        except ValueError:
            pass

        try:
            start_year, end_year = [int(e) for e in self.name.split('-')]
            pass
        except:
            pass
            
            
            


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
        from stats.models import Stat

        season_stats = Stat.objects.filter(competition=self.competition, season=self)
        return set([e[0] for e in season_stats.values_list("player_id")])


    def players_diff(self, season):
        ids = self.players() - season.players()
        return Bio.objects.filter(id__in=ids)

    def players_added(self):
        if self.previous_season():
            return self.players_diff(self.previous_season())
        return []

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


    def champion(self):
        from awards.models import AwardItem

        try:
            return AwardItem.objects.get(season=self, award__name='Champion')
        except:
            return None

    def mvp(self):
        from awards.models import AwardItem

        # Need to expand for other names.
        try:
            return AwardItem.objects.get(season=self, award__name='MVP')
        except:
            return None



    def data_string(self):
        s = ''
        if self.standing_set.exists():
            s += 'Sg'
        if self.stat_set.exists():
            s += 'St'
        if self.game_set.exists():
            s += 'Gm'
        if self.goal_set.exists():
            s += 'Gl'
        return s
            
