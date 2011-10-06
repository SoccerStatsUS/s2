from django.db import models

from s2.teams.models import Team
from s2.bios.models import Bio



class Stat(models.Model):
    """
    A stat for a competition. 
    Could in theory just be a single Game?
    """

    player = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)

    # Convert these soon.
    # It seems like there should be only one
    # competition field.
    competition = models.CharField(max_length=255)
    season = models.CharField(max_length=255)

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
        ordering = ('season', 'competition','games_started')
