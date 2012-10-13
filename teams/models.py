from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify


from collections import defaultdict

import datetime


class AbstractTeamManager(models.Manager):
    """
    An abstract Team Manager.
    """

    def recent_games(self, delta=datetime.timedelta(days=100)):
        """
        Returns a queryset of games played within a given timedelta.
        """
        since = datetime.date.today() - delta
        return self.get_query_set().filter(date__gte=since)

    def team_dict(self):
        """
        A dict mapping a team's name and short name to an id.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
            d[e.short_name] = e.id
        return d

    def duplicate_slugs(self):
        """
        Returns all teams with duplicate slugs.
        """
        # Used to find problem teams.
        d = defaultdict(list)
        for e in self.get_query_set():
            d[e.slug].append(e.name)
        return [(k, v) for (k, v) in d.items() if len(v) > 1]

            
    def find(self, name, create=False):
        """
        Given a team name, determine the actual team.
        """
        # This seems to duplicate alias functionality that is implemented in soccerdata.
        # Also, this looks a lot more time-consuming.

        #from soccer.teams.aliases import mapping
        teams = Team.objects.filter(name=name)
        if teams:
            return teams[0]

        teams = Team.objects.filter(short_name=name)
        if teams:
            return teams[0]

        if create:

            try:
                print "Creating %s" % name
            except:
                print "Created a team."

            team = Team.objects.create(
                name=name, 
                short_name=name, 
                )
            return team
        else:
            # Don't want to be creating teams all the time.
            raise


class TeamManager(AbstractTeamManager):
    """
    Normal Team Manager used for Team.objects.
    """


class DefunctTeamManager(AbstractTeamManager):
    """
    Team.defunct - teams that no longer exist.
    """

    def get_query_set(self):
        return super(DefunctTeamManager, self).get_query_set().filter(defunct=True, real=True)


class ActiveTeamManager(AbstractTeamManager):
    """
    Team.active - teams that no longer exist.
    """

    def get_query_set(self):
        return super(DefunctTeamManager, self).get_query_set().filter(defunct=False, real=True)

    


class RealTeamManager(AbstractTeamManager):
    """
    Team.real - teams that are not fictional.
    """

    def get_query_set(self):
        return super(RealTeamManager, self).get_query_set().filter(real=True)


class UnrealTeamManager(AbstractTeamManager):
    """
    Team.unreal - teams that are fictional.
    """

    def get_query_set(self):
        return super(RealTeamManager, self).get_query_set().filter(real=True)





class Team(models.Model):
    """
    A collection of players for a competition.
    """
    # Squads for, e.g. Champions League, World Cup?
    # Rolling roster for any team.
    # retirements.


    name = models.CharField(max_length=200, unique=True)

    # Affiliate team. e.g.
    # Portland Timbers Reserves -> Portland Timbers (reserve -> main)
    # Chicago Fire Select -> Chicago Fire (? affiliation)
    # United States -> United States U-20 (youth team)
    affiliate = models.ForeignKey('self', null=True)

    # Let's get rid of short name! It's really just another alias.
    # No way, it's useful when you want to display a better name.
    # Let's just be clear that it's very optional.
    short_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=False)
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

    awards = generic.GenericRelation('awards.AwardItem')


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
        """
        Returns a queryset of all players who have played for a team, with an optional season argument.
        """
        from stats.models import Stat
        from bios.models import Bio

        stats = Stat.objects.filter(team=self)
        if season:
            stats = stats.filter(season=season)

        player_ids = set([e[0] for e in stats.values_list('player')])
        return Bio.objects.filter(id__in=player_ids)


    def year_roster(self, year):
        """
        Generate a list of lists representing 

        Return something like this:
        http://www.flipflopflyin.com/flipflopflyball/info-1994expos.html
        """
        from s2.bios.models import Bio

        # Get all players for a given year.
        stats = self.stat_set.filter(season__name=year)
        player_ids = set()
        for stat in stats:
            player_ids.add(stat.player.id)

        return Bio.objects.filter(id__in=player_ids)


    def player_chart(self, year):
        roster = self.year_roster(year)
        
        years = []
        for player in roster:
            years_played = player.team_year_dict().keys()
            years.extend(years_played)

        years = sorted(set(years))

        l = []
        for e in roster:
            m = e.team_year_map(self, years)
            t = (e, m)
            l.append(t)

        return (years, l)



    def game_set(self):
        from games.models import Game
        return Game.objects.filter(models.Q(team1=self) | models.Q(team2=self))

    def team_stats(self):
        from stats.models import Stat
        return Stat.objects.filter(team=self, competition=None, season=None).exclude(minutes=0)


    def standings_by_date(self):
        return self.standing_set.exclude(season=None).order_by("season__name")


    def alltime_standing(self):
        """
        The alltime standing for a team.
        """
        # cache this?
        from standings.models import Standing
        return Standing.objects.get(team=self, competition=None, season=None)




        
            

