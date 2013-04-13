from collections import defaultdict
import datetime
import os

from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from places.models import City

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

    founded = models.DateField(null=True)
    dissolved = models.DateField(null=True)

    city = models.ForeignKey(City, null=True, blank=True)
    #city = models.CharField(max_length=255)

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



    def get_image(self):
        p = os.path.join("/home/chris/www/sdev/static/images/team/%s" % self.slug)
        exts = ['svg', 'png', 'gif', 'jpg']
        for ext in exts:
            fp = '%s.%s' % (p, ext)
            if os.path.exists(fp):
                return fp.split('sdev')[1]
        return ''


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


    def previous_game(self, game):
        from games.models import Game

        if game.date is None:
            return None

        games = Game.objects.team_filter(self).filter(date__lt=game.date, season=game.season).order_by('-date')
        if games:
            return games[0]
        else:
            return None
    
    def next_game(self, game):
        from games.models import Game

        if game.date is None:
            return None

        games = Game.objects.team_filter(self).filter(date__gt=game.date, season=game.season).order_by('date')
        if games:
            return games[0]
        else:
            return None
        

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
        from stats.models import TeamStat
        return Stat.objects.filter(team=self).exclude(minutes=0)


    def standings_by_date(self):
        return self.standing_set.exclude(season=None).order_by("season__name")


    def alltime_standing(self):
        """
        The alltime standing for a team.
        """
        # cache this?
        from standings.models import Standing
        return Standing.objects.get(team=self, competition=None, season=None)



    def form(self, start_game=None, count=5, competition=None, season=None, include_start=True):
        if start_game is None:
            start_game = self.game_set().order_by('-date')[0]

        games = self.game_set().exclude(date=None).order_by('-date')
        if include_start:
            games = games.filter(date__lte=start_game.date).order_by('-date')
        else:
            games = games.filter(date__lt=start_game.date).order_by('-date')


        if competition:
            games = games.filter(competition=competition)

        if season:
            games = games.filter(season=season)

        return self.result_string(games[:count])

    def result_string(self, games):
        s = ''
        for game in games:
            s += game.result(self)
        return s
            


class TeamAlias(models.Model):        
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=200, unique=True)
    
    start = models.DateField()
    end = models.DateField()
    
            

