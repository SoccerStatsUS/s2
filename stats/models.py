from django.db import models

from s2.bios.models import Bio
from s2.competitions.models import Competition, Season
from s2.games.models import Game
from s2.lineups.models import Appearance
from s2.teams.models import Team

import datetime
from collections import defaultdict


class StatsManager(models.Manager):

    # Regular season stats.

    def get_query_set(self):
        # This is important.
        return super(StatsManager, self).get_query_set().exclude(team=None).exclude(season=None)


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
        return super(PositionStatsManager, self).get_query_set().filter(team=None, season=None, competition=None, position=None)


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
    # Team should be optional
    # Stats should be generated from data.
    # Stats should be regenerated on Game, Goal, etc. scoring.
    # Standings should sort of be generated the same way.
    

    # Probably these should be represented differently.
    game = models.ForeignKey(Game, null=True)
    player = models.ForeignKey(Bio, null=True)
    team = models.ForeignKey(Team, null=True)
    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season, null=True)

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
    

    def __unicode__(self):
        return "%s, %s, %s, %s" % (self.game, self.player, self.team, self.season)


    def shooting_percentage(self):
        return self.goals / float(self.asists)


    def goals_per_90(self):
        return 90 * self.goals / float(self.minutes)


    def plus_minus_per_90(self):
        return 90 * self.plus_minus / float(minutes)



    def goal_proportion(self):
        """
        Proportion of all game goals that a player was involved in.
        """
        return self.goals / float(self.goals_for)




    



    class Meta:
        ordering = ('season__name', 'competition', '-games_played', '-goals')
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

        self.wins = d['win']
        self.losses = d['loss']
        self.ties = d['tie']
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
            return [self.game.home_team, self.game.away_team]

        if self.player:
            appearances = Appearance.objects.filter(player=self.player)
            team_ids = set([e[0] for e in appearances.values_list('team')])
            teams = x
            games = games.filter(id__in=game_ids)


    def age(self):
        # Fix this.
        if self.player.birthdate:
            return (datetime.date.today() - self.player.birthdate).days / 365.0
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


            
            

        

