from django.db import models

from s2.teams.models import Team
from s2.bios.models import Bio
from s2.competitions.models import Competition, Season


class CareerStatsManager(models.Manager):

    def get_query_set(self):
        return super(CareerStatsManager, self).get_query_set().filter(team=None, season=None)


class CompetitionStatsManager(models.Manager):

    def get_query_set(self):
        return super(CompetitionStatsManager, self).get_query_set().filter(team=None).exclude(competition=None)


class TeamStatsManager(models.Manager):

    def get_query_set(self):
        return super(TeamStatsManager, self).get_query_set().filter(season=None).exclude(team=None)


class StatsManager(models.Manager):

    def get_query_set(self):
        return super(StatsManager, self).get_query_set().exclude(team=None).exclude(season=None)


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
    

    player = models.ForeignKey(Bio, null=True)
    team = models.ForeignKey(Team, null=True)

    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season, null=True)

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

    objects = StatsManager()
    team_stats = TeamStatsManager()
    career_stats = CareerStatsManager()
    competition_stats = CompetitionStatsManager()

    def __unicode__(self):
        return "stat"
        #return "%s, %s, %s, %s" % (self.player, self.team, self.competition, self.season)


    class Meta:
        ordering = ('season__name', 'competition', 'player')
        #unique_together = ('player', 'team', 'competition', 'season')

