from django.db import models

from s2.teams.models import Team
from s2.bios.models import Bio
from s2.competitions.models import Competition, Season



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

    class Meta:
        ordering = ('season__name', 'competition')
        #unique_together = ('player', 'team', 'competition', 'season')
