from django.db import models
from django.template.defaultfilters import slugify


from s2.teams.models import Team
from s2.bios.models import Bio

from collections import defaultdict

class PositionManager(models.Manager):

    def generate_standings(self):
        # Pick a name!! standings or stats!!
        for e in self.get_query_set():
            try:
                e.generate_standings()
            except:
                print "failed on %s" % e.id


    def distinct_names(self):
        return sorted(set([(e.name, e.slug) for e in Position.objects.all()]))

    

class Position(models.Model):
    # Something like Peter Wilt, Chicago Fire, 2010, 2011

    person = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)

    name = models.CharField(max_length=255)

    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    slug = models.SlugField()

    objects = PositionManager()

    def __unicode__(self):
        return "%s, %s, %s" % (self.person, self.team, self.name)

    def save(self, *args, **kwargs):
        # Is this a good idea?
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Position, self).save(*args, **kwargs)



    def games(self):
        from s2.games.models import Game


        if self.start is None and self.end is None:
            return []

        games = Game.objects.team_filter(self.team)

        if self.start:
            games = games.filter(date__gte=self.start)

        if self.end:
            games = games.filter(date__lte=self.end)

        return games


    def generate_standings(self):
        """
        Generate the stats for a given position.
        """
        from s2.stats.models import Stat

        d = {}
        for game in self.games():

            # Add relevant season data if not set.
            season = game.season
            if season not in d:
                d[season] = defaultdict(int)

            dx = d[season]
            result = game.result(self.team)
            dx[result] += 1
            try:
                dx['goals_for'] += game.goals_for(self.team)
                dx['goals_against'] += game.goals_against(self.team)
            except:
                print "FAIL"

        for season, dx in d.items():
            Stat.objects.create(
                team=self.team,
                player=self.person,
                position=self.name,
                season=season,
                competition=season.competition,
                wins=dx['win'],
                losses=dx['loss'],
                ties=dx['tie'],
                goals_for=dx['goals_for'],
                goals_against=dx['goals_against'],
                plus_minus=dx['plus_minus'],
                )
                





    class Meta:
        ordering = ('start', )
