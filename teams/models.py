from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

import datetime


class DefunctTeamManager(models.Manager):
    def get_query_set(self):
        return super(DefunctTeamManager, self).get_query_set().filter(defunct=True, real=True)


class RealTeamManager(models.Manager):
    def get_query_set(self):
        return super(RealTeamManager, self).get_query_set().filter(real=True)


class TeamManager(models.Manager):

    def recent_games(self, delta=datetime.timedelta(days=100)):
        since = datetime.date.today() - delta
        return self.get_query_set().filter(date__gte=since)

    def team_dict(self):
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
            d[e.short_name] = e.id
        return d
            
                         

    def find(self, name, create=False):
        """
        Given a team name, determine the actual team.
        """
        if name == u'':
            import pdb; pdb.set_trace()

        #from soccer.teams.aliases import mapping
        teams = Team.objects.filter(name=name)
        if teams:
            return teams[0]

        teams = Team.objects.filter(short_name=name)
        if teams:
            return teams[0]

        if create:
            print "Creating %s" % name
            team = Team.objects.create(
                name=name, 
                short_name=name, 
                )
            return team
        else:
            # Don't want to be creating teams all the time.
            raise




class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # Let's get rid of short name! It's really just another alias.
    # No way, it's useful when you want to display a better name.
    # Let's just be clear that it's very optional.
    short_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=False)
    founded = models.IntegerField(null=True, blank=True)

    # Not sure if we want this here.
    # Some teams can have multiple cities?
    city = models.CharField(max_length=255)

    # Have some virtual teams from USMNT drafts.
    real = models.BooleanField(default=True)
    defunct = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    objects = TeamManager()
    defuncts = DefunctTeamManager()
    reals = RealTeamManager()


    class Meta:
        ordering = ('short_name',)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.short_name)
            
        super(Team, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('team_detail', args=[self.slug])



    def fancy_name(self):
        return self.name

    @property
    def normal_name(self):
        if self.short_name:
            return self.short_name
        return self.name

    def __unicode__(self):
        return self.short_name

    def roster(self, season=None):
        from s2.stats.models import Stat
        from s2.bios.models import Bio
        player_ids = set([e[0] for e in Stat.objects.filter(team=self).values_list('player')])
        return Bio.objects.filter(id__in=player_ids)


    def game_set(self):
        from s2.games.models import Game
        return Game.objects.filter(models.Q(home_team=self) | models.Q(away_team=self))

    def team_stats(self):
        from stats.models import Stat
        return Stat.objects.filter(team=self, competition=None, season=None).exclude(minutes=0)


    def standings_by_date(self):
        return self.standing_set.exclude(season=None).order_by("season__name")


    def alltime_standing(self):
        from s2.standings.models import Standing
        return Standing.objects.get(team=self, competition=None, season=None)
