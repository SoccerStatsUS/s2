from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.template.defaultfilters import slugify

from functools import lru_cache
from collections import defaultdict
import datetime

import random
from django.urls import reverse


class BioManager(models.Manager):

    def born_on(self, month, day):
        """
        Returns the most notable person born on this day:
        hall of famers first, then most career games played.
        """
        b = self.get_queryset().filter(birthdate__month=month, birthdate__day=day)
        return b.order_by(
            '-hall_of_fame',
            models.F('careerstat__games_played').desc(nulls_last=True)).first()
        
        

    def bio_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for name, eid in self.get_queryset().values_list('name', 'id'):
            d[name] = eid
        return d

    def bio_dictx(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
        return d


    def find(self, name, create=True):
        """
        Given a team name, determine the actual team.
        """
        # Not here?
        if name == '':
            import pdb; pdb.set_trace()
        
        bios = Bio.objects.filter(name=name)
        if bios:
            return bios[0]
        else:
            return Bio.objects.create(name=name, hall_of_fame=False)


    def duplicate_slugs(self):
        """
        Returns all bios with duplicate slugs.
        """
        # Used to find problem bios.
        d = defaultdict(list)
        for e in self.get_queryset():
            d[e.slug].append(e.name)
        return [k for (k, v) in d.items() if len(v) > 1]


    def reverse_names(self):
        """
        Returns all bios with duplicate slugs.
        """

        # Do this in pairs.

        #def rv(s):
        #    first, last = s.split(' ', 1)
        #    return "%s %s" % (last, first)

        regular_names = set(self.get_queryset().values_list('name', flat=True))

        reversed_names = set()
        for e in self.get_queryset().filter(name__contains=' ').values_list('name', flat=True):
            reversed_names.add(s)

        tmp = regular_names.intersection(reversed_names)
        final = set()

    def id_to_slug(self, pid):
        return Bio.objects.get(id=pid).slug

    # id_to_slug = lru_cache(id_to_slug, {}, 2)


class Bio(models.Model):
    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=False)

    height = models.IntegerField(null=True, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    birthplace = models.ForeignKey('places.City', null=True, blank=True, related_name='birth_set', on_delete=models.CASCADE)
    birth_country = models.ForeignKey('places.Country', null=True, blank=True, related_name='citizen_set', on_delete=models.CASCADE)

    deathdate = models.DateField(null=True, blank=True)
    deathplace = models.ForeignKey('places.City', null=True, blank=True, related_name='death_set', on_delete=models.CASCADE)

    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    awards = GenericRelation('awards.AwardItem')
    images = GenericRelation('images.Image')

    #position = models.CharField(max_length=20)

    # This doesn't need to be here, but is for filtering / convenience purposes.
    hall_of_fame = models.BooleanField() # Whether or not a player is in the hall of fame.



    objects = BioManager()


    class Meta:
        pass
        #ordering = ('name',)



    def get_image(self):
        import os

        p = os.path.join("/home/chris/www/sdev/static/images/people/%s" % self.slug)
        exts = ['svg', 'png', 'gif', 'jpg']
        for ext in exts:
            fp = '%s.%s' % (p, ext)
            if os.path.exists(fp):
                return fp.split('sdev')[1]
        return ''

    def ref_set(self):
        from games.models import Game
        return Game.objects.filter(referee=self)

    def assistant_ref_set(self):
        from games.models import Game
        query = models.Q(linesman3=self) | models.Q(linesman2=self) | models.Q(linesman3=self)
        return Game.objects.filter(query)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.slug])



    def height_display(self):
        # Heights are stored as inches or centimeters depending on the source.
        if not self.height:
            return None
        inches = self.height if self.height <= 90 else round(self.height / 2.54)
        return "%d'%d\"" % divmod(inches, 12)

    def weight_display(self):
        # Weights are stored as pounds or kilograms depending on the source.
        if not self.weight:
            return None
        pounds = self.weight if self.weight > 100 else round(self.weight * 2.20462)
        return '%s lbs' % pounds

    def first_game(self):

        from lineups.models import Appearance
        try:
            return Appearance.objects.filter(player=self).exclude(game__date=None).order_by('game__date')[0].game
        except:
            return None


    def last_game(self):        
        from lineups.models import Appearance
        try:
            return Appearance.objects.filter(player=self).exclude(game__date=None).order_by('-game__date')[0].game
        except: 
            return None


    def team_year_dict(self):
        d = defaultdict(set)
        for e in self.stat_set.all():
            d[e.season.name].add(e.team)

        return d


    def team_year_map(self, team, year_list):
        d = self.team_year_dict()
        l = []
        
        # Code three possibilities (player did not player that year,
        # player played for a different team,
        # player played for the same team
        for year in year_list:
            if year not in d:
                l.append(0)
            elif team not in d[year]:
                l.append(1)
            else:
                l.append(2)
        return l
        

    def usmnt_draft_picks(self):
        """
        Return a list of picks where the player has been selected in the USMNT draft.
        """
        return self.pick_set.filter(draft__name__contains='USMNT')



    def save(self, *args, **kwargs):
        # Is this a good idea?
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Bio, self).save(*args, **kwargs)


    def age(self, date=None):
        """
        Returns a player's age in days from a given day.
        Default is today.
        """

        if date is None:
            date = datetime.date.today()

        if self.birthdate:
            return date - self.birthdate
        else:
            return None


    def age_years(self, date=None):
        """
        Returns a player's age in years (approximately)
        """
        a = self.age(date)
        if a:
            return a.days / 365.25
        else:
            return None


    def age_display(self, date=None):
        """
        Returns a player's age in whole years.
        """
        a = self.age_years(date)
        if a is None:
            return None
        return int(a)


    def season_stats(self):
        """
        All stats for a player that are for a single season.
        (Contrast with career stats)
        """
        from stats.models import SeasonStat
        return SeasonStat.objects.filter(player=self)


    #def domestic_season_stats(self):
    #    return self.season_stats.filter(

    def season_stats_with_totals(self):
        from stats.models import Stat
        return Stat.all_stats.exclude(team=None).exclude(competition=None).filter(player=self)


    def position_stats(self):
        return []


    def career_stat(self):
        """
        Summary stats for a player's entire career.
        """
        from stats.models import CareerStat

        try:
            return CareerStat.objects.get(player=self)
        except:
            return None

    def career_stats(self):
        """
        Wrapper to make including career_stat in templates easier.
        """
        return [self.career_stat()]

    def competition_stats(self):
        """
        Summary stats for a player in a given competition (e.g. MLS)
        """
        from stats.models import CompetitionStat

        return CompetitionStat.objects.filter(player=self)

    def team_stats(self):
        """
        Summary stats for a player in a given competition (e.g. MLS)
        """
        from stats.models import TeamStat

        return TeamStat.objects.filter(player=self)


    def calculate_standings(self):
        """
        Generate standings for a given player.
        """
        from stats.models import Stat

        # Calculate standings for any stat that doesn't have it already.
        # (season stats only, not summary stats.
        for stat in self.stat_set.all():
            if stat.wins is None:
                stat.calculate_standings()

        # Generate career standings if 1. it exists and 2. hasn't been generated yet.
        if self.career_stat() and self.career_stat().wins is None:
            self.career_stat().calculate_standings()

        # Generate summary team standings.
        team_stats = TeamStat.objects.filter(player=self)
        for stat in team_stats:
            if stat.wins is None:
                stat.calculate_standings()


    def find_data(self):
        # A utility method to find where a bio is coming from.
        # Used to kill duplicates.

        l = []
        for method in dir(self):
            if not method.startswith('_'):
                try:
                    m = getattr(self, method)
                    if 'all' in dir(m) and m.all():
                        t = (method, m.all())
                        l.append(t)
                except:
                    pass
        return l
            






