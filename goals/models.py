from collections import defaultdict

from django.db import models

from bios.models import Bio
from games.models import Game
from teams.models import Team


class GoalManager(models.Manager):

    def frequency(self):
        """
        Returns a list of goal counts by minute.
        [{1: 91, 2: 30, ...}]
        """
        d = defaultdict(int)
        for goal in Goal.objects.all():
            d[goal.minute] += 1
        return d
        

class Goal(models.Model):
    """
    Represents a completed game.
    """

    date = models.DateField() # This shouldn't be here. Game can tell us the date.
    minute = models.IntegerField(null=True)
    team = models.ForeignKey(Team)
    player = models.ForeignKey(Bio)
    game = models.ForeignKey(Game, null=True)

    penalty = models.BooleanField(default=False)
    own_goal = models.BooleanField(default=False)

    objects = GoalManager()
    
    class Meta:
        ordering = ('game', '-minute', 'team')

    def opponent(self):
        if self.team == self.game.home_team:
            return self.game.away_team
        else:
            return self.game.home_team
 

    def __unicode__(self):
        return u"%s: %s (%s)" % (self.game.date, self.player, self.minute)





