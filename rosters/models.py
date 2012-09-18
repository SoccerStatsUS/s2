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


class RosterManager(models.Manager):


    def get_query_set(self):
        # This is important.
        return super(RosterManager, self).get_query_set()


class Roster(models.Model):
    """
    A stat for a competition. 
    Could in theory just be a single Game?
    """

    team = models.ForeignKey(Team, null=True)
    #date = models.CharField


class RosterMember(models.Model):
    
    roster = models.ForeignKey(Roster)
    person = models.ForeignKey(Bio)


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

    objects = RosterManager()

    def __unicode__(self):
        return "%s, %s, %s, %s" % (self.game, self.player, self.team, self.season)



            
            

        

"""
