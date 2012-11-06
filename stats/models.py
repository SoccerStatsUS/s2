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


class AbstractStat(models.Model):

    #game = models.ForeignKey(Game, null=True)
    #player = models.ForeignKey(Bio, null=True)
    #team = models.ForeignKey(Team, null=True)
    #competition = models.ForeignKey(Competition, null=True)
    #season = models.ForeignKey(Season, null=True)

    #position = models.CharField(max_length=255, null=True)
    # Position should probably be a ForeignKey to Position.

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

    # Should these be in standing? Probably not.
    # Probably should merge standing into here.
    # plus_minus should be a method? Probably not.
    plus_minus = models.IntegerField(null=True, blank=True)
    goals_for = models.IntegerField(null=True, blank=True)
    goals_against = models.IntegerField(null=True, blank=True)

    wins = models.IntegerField(null=True, blank=True)
    ties = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)

    source = models.ForeignKey(Source, null=True)

    class Meta:
        abstract = True


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


            
    def win_percentage(self):
        if not self.games:
            return None
        ties = self.ties or 0
        return (self.wins + .5 * ties) / self.games

    def win_percentage_100(self):
        if self.win_percentage() is None:
            return None
        return self.win_percentage() * 100



    def partnerships(self, competition, season):
        stats = Stat.objects.filter(competition=competition, season=season)
        teams = set([e[0] for e in stats.values_list('team')])

        l = []
        for team_id in teams:
            team = Team.objects.get(id=team_id)
            tstats = stats.filter(team=team_id).exclude(goals=None).order_by('-goals')
            pair = tstats[:2]
            goals = tstats[0].goals + tstats[1].goals
            t = (goals, competition, season, team, tstats[0].player, tstats[1].player)
            l.append(t)
        return l
            



class CareerStat(AbstractStat):
    # Should rename player person?
    player = models.ForeignKey(Bio)


class CompetitionStat(AbstractStat):
    player = models.ForeignKey(Bio)
    competition = models.ForeignKey(Competition)

class TeamStat(AbstractStat):
    player = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)


class SeasonStat(AbstractStat):
    player = models.ForeignKey(Bio)
    competition = models.ForeignKey(Competition) # Redundancy
    season = models.ForeignKey(Season)


class Stat(AbstractStat):
    player = models.ForeignKey(Bio)
    competition = models.ForeignKey(Competition) # Redundancy
    season = models.ForeignKey(Season)
    team = models.ForeignKey(Team)
