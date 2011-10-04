from django.db import models

from s2.bios.models import Bio
from s2.games.models import Game
from s2.teams.models import Team

class Goal(models.Model):
    """
    Represents a completed game.
    """
    # Should we have a date and a datetime field?
    date = models.DateField()
    minute = models.IntegerField()
    team = models.ForeignKey(Team)
    player = models.ForeignKey(Bio)
    game = models.ForeignKey(Game)

    penalty = models.BooleanField(default=False)
    own_goal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('date', 'team', 'minute')
 

    def __unicode__(self):
        return u"%s: %s (%s)" % (self.date, self.player, self.minute)



