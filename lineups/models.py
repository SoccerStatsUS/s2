from django.db import models

from s2.bios.models import Bio
from s2.games.models import Game
from s2.teams.models import Team

class Appearance(models.Model):

    player = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)
    game = models.ForeignKey(Game)

    #on = models.IntegerField()
    #off = models.IntegerField()
    on = models.CharField(max_length=255)
    off = models.CharField(max_length=255)