from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from games.models import Game
from lineups.models import Appearance
from positions.models import Position
from sources.models import Source
from teams.models import Team

import datetime
from collections import defaultdict

from django.core.cache import cache


class StandingStat(models.Model):

    # Should these be in standing? Probably not.
    # Probably should merge standing into here.
    # plus_minus should be a method? Probably not.
    plus_minus = models.IntegerField(null=True, blank=True)
    goals_for = models.IntegerField(null=True, blank=True)
    goals_against = models.IntegerField(null=True, blank=True)

    games = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(null=True, blank=True)
    ties = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)

            
    def win_percentage(self):
        if not self.games:
            return None
        ties = self.ties or 0
        return (self.wins + .5 * ties) / self.games

    def win_percentage_100(self):
        if self.win_percentage() is None:
            return None
        return self.win_percentage() * 100


    class Meta:
        abstract = True



class AbstractStat(StandingStat):

    #game = models.ForeignKey(Game, null=True)
    #player = models.ForeignKey(Bio, null=True)
    #team = models.ForeignKey(Team, null=True)
    #competition = models.ForeignKey(Competition, null=True)
    #season = models.ForeignKey(Season, null=True)

    #position = models.CharField(max_length=255, null=True)
    # Position should probably be a ForeignKey to Position.


    games_started = models.IntegerField(null=True, blank=True)
    games_played = models.IntegerField(null=True, blank=True)
    minutes = models.IntegerField(null=True, blank=True)

    goals = models.IntegerField(null=True, blank=True)
    own_goals = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    shots = models.IntegerField(null=True, blank=True)
    shots_on_goal = models.IntegerField(null=True, blank=True)

    fouls_committed = models.IntegerField(null=True, blank=True)
    fouls_suffered = models.IntegerField(null=True, blank=True)
    yellow_cards = models.IntegerField(null=True, blank=True)
    red_cards = models.IntegerField(null=True, blank=True)

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
            

class GameStat(AbstractStat):
    player = models.ForeignKey(Bio)
    game = models.ForeignKey(Game)
    team = models.ForeignKey(Team)

    age = models.FloatField(null=True) # Age in years at the time of game.
    on = models.IntegerField(null=True)
    off = models.IntegerField(null=True)

    result = models.CharField(max_length=5)

    def score_or_result(self):
        if self.team == self.game.team1:
            return self.game.score_or_result()
        else:
            return self.game.reverse_score_or_result()

    @property
    def goal_differential(self):
        try:
            return self.goals_for - self.goals_against
        except:
            return None

    def opponent(self):
        if self.team == self.game.team1:
            return self.game.team2
        else:
            return self.game.team1

    def team_original_name(self):
        if self.team == self.game.team1:
            return self.game.team1_original_name
        else:
            return self.game.team2_original_name

    def opponent_original_name(self):
        if self.team == self.game.team1:
            return self.game.team2_original_name
        else:
            return self.game.team1_original_name


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


class TeamCompetitionStat(AbstractStat):
    player = models.ForeignKey(Bio)
    competition = models.ForeignKey(Competition)
    team = models.ForeignKey(Team)


class Stat(AbstractStat):
    player = models.ForeignKey(Bio)
    competition = models.ForeignKey(Competition) # Redundancy
    season = models.ForeignKey(Season)
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return u"%s: %s/%s/%s" % (self.player, self.competition, self.season.name, self.team)


# Still having trouble figuring out exactly where to put this data.
class CoachStat(StandingStat):

    person = models.ForeignKey(Bio)
    #position = models.ForeignKey(Position)
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)
    team = models.ForeignKey(Team)


    # Should these be in standing? Probably not.
    # Probably should merge standing into here.
    # plus_minus should be a method? Probably not.

    #plus_minus = models.IntegerField(null=True, blank=True)
    #goals_for = models.IntegerField(null=True, blank=True)
    #goals_against = models.IntegerField(null=True, blank=True)

    #wins = models.IntegerField(null=True, blank=True)
    #ties = models.IntegerField(null=True, blank=True)
    #losses = models.IntegerField(null=True, blank=True)


class CoachTeamStat(StandingStat):

    person = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)
