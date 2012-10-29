from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from games.models import Game
from lineups.models import Appearance
from sources.models import Source
from teams.models import Team

import datetime
from collections import defaultdict

from django.core.cache import cache


class StatsManager(models.Manager):

    # Regular season stats.

    def get_query_set(self):
        # This is important.
        return super(StatsManager, self).get_query_set().exclude(team=None).exclude(season=None).filter(position=None)



class AllStatsManager(models.Manager):

    # Regular season stats.

    def get_query_set(self):
        # This is important.
        return super(AllStatsManager, self).get_query_set()


class CareerStatsManager(models.Manager):

    # Stats for an entire career

    def get_query_set(self):
        return super(CareerStatsManager, self).get_query_set().filter(team=None, season=None, competition=None, position=None)

    def to_dict(self):
        d = {}
        for e in self.get_query_set():
            d[e.player] = e
        return d


class PositionStatsManager(models.Manager):

    # Stats for non-players (coaches, owners, etc.)
    # Primarily WLT, GF, GA

    def get_query_set(self):
        return super(PositionStatsManager, self).get_query_set().exclude(position=None)


class CompetitionStatsManager(models.Manager):

    # Stats for a given competition across all competitions

    def get_query_set(self):
        return super(CompetitionStatsManager, self).get_query_set().filter(team=None).exclude(competition=None)


class TeamStatsManager(models.Manager):

    # Stats for a given team across all season

    def get_query_set(self):
        return super(TeamStatsManager, self).get_query_set().filter(season=None).exclude(team=None)


class Stat(models.Model):
    """
    A stat for a competition. 
    Could in theory just be a single Game?
    """

    # What do we need from this model?
    # Stats should be regenerated on Game, Goal, etc. scoring.
    # Standings should sort of be generated the same way.

    game = models.ForeignKey(Game, null=True)
    player = models.ForeignKey(Bio, null=True)
    team = models.ForeignKey(Team, null=True)
    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season, null=True)

    source = models.ForeignKey(Source, null=True)

    position = models.CharField(max_length=255, null=True)

    minutes = models.IntegerField(null=True, blank=True)
    games_started = models.IntegerField(null=True, blank=True)
    games_played = models.IntegerField(null=True, blank=True)
    goals = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    shots = models.IntegerField(null=True, blank=True)
    shots_on_goal = models.IntegerField(null=True, blank=True)
    fouls_committed = models.IntegerField(null=True, blank=True)
    fouls_suffered = models.IntegerField(null=True, blank=True)
    yellow_cards = models.IntegerField(null=True, blank=True)
    red_cards = models.IntegerField(null=True, blank=True)

    # plus_minus should be a method.
    plus_minus = models.IntegerField(null=True, blank=True)
    goals_for = models.IntegerField(null=True, blank=True)
    goals_against = models.IntegerField(null=True, blank=True)

    wins = models.IntegerField(null=True, blank=True)
    ties = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)

    offense_score = models.FloatField(null=True, blank=True)
    defense_score = models.FloatField(null=True, blank=True)

    objects = StatsManager()
    
    position_stats = PositionStatsManager()
    
    team_stats = TeamStatsManager()
    career_stats = CareerStatsManager()
    competition_stats = CompetitionStatsManager()

    all_stats = AllStatsManager()
    

    def __unicode__(self):
        return u"%s, %s, %s, %s" % (self.game, self.player, self.team, self.season)


    def assistiness(self):
        """This measures the proportion of a hypothetical average team's assists a player
        accounted for. e.g. if a player's rating is .3, that means he accounted for 30% of a team's
        expected assists that year. Designed to combat standard assist bias."""
        # This is way too slow.
        

        def season_adjustment_factor():
            # This should hang off season. And probably be memoized?

            def _id(m):
                if m is None:
                    return None
                else:
                    return m.id

            key = "assistiness:%s:%s" % (_id(self.season), _id(self.competition))
            
            i = cache.get(key)
            if i is None:
                season_stats = Stat.objects.filter(season=self.season, competition=self.competition)
                if season_stats.count() == 0:
                    i = None
                else:
                    total_assists = sum([e.assists for e in season_stats if e.assists])
                    teams = set([e.team for e in season_stats])
                    team_count_float = float(len(teams))
                    i = team_count_float / total_assists
                cache.set(key, i, 24 * 60 * 60)
            
            return i

        if self.assists == 0:
            return 0

        f = season_adjustment_factor()
        if f is None:
            return None
        else:
            return self.assists * f
            






        return (float(self.assists) * len(teams)) / total_assists



        


    def shooting_percentage(self):
        return self.goals / float(self.asists)


    def goals_per_90(self):
        if self.minutes == 0:
            return 0
        return 90 * self.goals / float(self.minutes)


    def assists_per_90(self):
        if self.minutes == 0:
            return 0
        return 90 * self.goals / float(self.minutes)

    def goals_assists_per_90(self):
        return self.goals_per_90() + self.assists_per_90()



    def plus_minus_per_90(self):
        if not self.minutes:
            return 0
        return 90 * self.plus_minus / float(self.minutes)





    def goal_proportion(self):
        """
        Proportion of all game goals that a player was involved in.
        """
        return self.goals / float(self.goals_for)




    



    class Meta:
        ordering = ('competition', 'season__name', '-games_played', '-goals')
        #unique_together = ('player', 'team', 'competition', 'season')


    def appearances(self):
        if self.game:
            if self.player:
                return Appearance.objects.filter(game=self.game, player=self.player)
            else:
                return Appearance.objects.filter(game=self.game)

        if self.team:
            appearances = Appearance.objects.filter(team=self.team)
        else:
            appearances = Appearance.objects.all()

        if self.player:
            appearances = appearances.filter(player=self.player)

        if self.competition:
            appearances = appearances.filter(game__competition=self.competition)

        if self.season:
            appearances = appearances.filter(game__season=self.season)

        return appearances


    def calculate_standings(self):
        d = defaultdict(int)
        for a in self.appearances():
            result = a.result
            d[result] += 1
            try:
                d['goals_for'] += a.goals_for
                d['goals_against'] += a.goals_against
            except:
                print "FAIL"

        self.wins = d['w']
        self.losses = d['l']
        self.ties = d['t']
        self.goals_for = d['goals_for']
        self.goals_against = d['goals_against']
        self.plus_minus = self.goals_for - self.goals_against

        try:
            self.save()
        except:
            print self
            print "Can't save"

        

    def teams(self):

        if self.team:
            return [self.team]
        
        if self.game:
            return [self.game.team1, self.game.team2]

        if self.player:
            appearances = Appearance.objects.filter(player=self.player)
            team_ids = set([e[0] for e in appearances.values_list('team')])
            teams = x
            games = games.filter(id__in=game_ids)


    def get_age(self):
        # Handle cases '2002' and '2002-2003'

        #import pdb; pdb.set_trace()
        
        if self.season is None:
            return None

        if self.season and self.season.average_date():
            dt = self.season.average_date()
            d = datetime.date(dt.year, dt.month, dt.day)

        else:
            if '-' in self.season.name:
                try:
                    first, second = [int(e) for e in self.season.name.split('-')]
                    d = datetime.date(second, 1, 1)
                except:
                    return None

            else:
                try:
                    year = int(self.season.name)
                    d = datetime.date(year, 7, 1)
                except:
                    return None


        if self.player.birthdate:
            return (d - self.player.birthdate).days / 365.0
        return None
        
        

    @property
    def games(self):
        return self.wins + self.ties + self.losses

            
    def win_percentage(self):
        if not self.games:
            return None
        ties = self.ties or 0
        return (self.wins + .5 * ties) / self.games

    def win_percentage_100(self):
        if self.win_percentage() is None:
            return None
        return self.win_percentage() * 100


            
            

        

