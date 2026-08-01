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


# This is very similar to Position
# These could probably be merged similar to stats.



class RosterItem(models.Model):
    """
    A tenure of a person with a given team.
    """
    
    person = models.ForeignKey(Bio, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start = models.DateField()
    end = modelsDateField()


class Transfer(models.Model):
    """
    Represents a transfer from one team to another team.
    """

    person = models.ForeignKey(Bio, on_delete=models.CASCADE)
    src = models.ForeignKey(Team, on_delete=models.CASCADE)
    dst = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateField(null=True)

    
