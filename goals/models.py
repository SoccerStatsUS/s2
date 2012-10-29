from collections import defaultdict

from django.db import models

from bios.models import Bio
from games.models import Game
from teams.models import Team


class GoalManager(models.Manager):

    def unique_dict(self):
        d = {}
        for e in self.get_query_set():
            player_id = own_goal_player_id = None
            if e.player:
                player_id = e.player.id

            if e.own_goal_player:
                own_goal_player_id = e.own_goal_player.id

            key = (e.team.id, player_id, own_goal_player_id, e.minute, e.date)
            d[key] = e.id
        return d


    def frequency(self):
        """
        Returns a list of goal counts by minute.
        [{1: 91, 2: 30, ...}]
        """
        minutes = [e[0] for e in Goal.objects.values_list('minute')]
        
        d = defaultdict(int)
        for minute in minutes:
            d[minute] += 1
        return d

        

class Goal(models.Model):
    """
    Represents a completed game.
    """

    date = models.DateField() # This shouldn't be here. Game can tell us the date.
    minute = models.IntegerField(null=True)
    team = models.ForeignKey(Team)
    team_original_name = models.CharField(max_length=255)
    
    player = models.ForeignKey(Bio, null=True)
    own_goal_player = models.ForeignKey(Bio, null=True, related_name='own_goal_set')

    game = models.ForeignKey(Game, null=True)

    penalty = models.BooleanField(default=False)
    own_goal = models.BooleanField(default=False)


    objects = GoalManager()
    
    class Meta:
        ordering = ('game', '-minute', 'team')

    def opponent(self):
        if self.team == self.game.team1:
            return self.game.team2
        else:
            return self.game.team1


    def result(self):
        return self.game.result(self.team)


 

    def __unicode__(self):
        return u"%s: %s (%s)" % (self.game.date, self.player, self.minute)



class Assist(models.Model):
    
    goal = models.ForeignKey(Goal)
    player = models.ForeignKey(Bio)

    # Primary assist (1), secondary assist (2), ad infinitum.
    # Goals and assists could be represented with the same object.
    order = models.IntegerField()

