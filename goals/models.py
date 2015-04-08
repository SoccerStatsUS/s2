from collections import defaultdict

from django.db import models

from bios.models import Bio
from games.models import Game
from teams.models import Team


class GoalManager(models.Manager):

    def unique_dict(self):
        d = {}
        for pid, ogpid, tid, minute, date, eid in self.get_queryset().values_list("player", "own_goal_player", "team", "minute", "date", "id"):
            key = (tid, pid, ogpid, minute, date)
            d[key] = eid
        return d

    def unique_dict_old(self):
        d = {}
        for e in self.get_queryset():
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
    #team_original_name = models.CharField(max_length=255)
    
    # There should only be player.
    player = models.ForeignKey(Bio, null=True)
    own_goal_player = models.ForeignKey(Bio, null=True, related_name='own_goal_set')

    game = models.ForeignKey(Game, null=True)

    penalty = models.BooleanField(default=False)
    own_goal = models.BooleanField(default=False)


    objects = GoalManager()
    
    class Meta:
        ordering = ('game', 'minute', 'team')


    """Inherit from common subclass - Goal, Appearance..."""
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

    def score_or_result(self):
        if self.team == self.game.team1:
            return self.game.score_or_result()
        else:
            return self.game.reverse_score_or_result()




    def result(self):
        return self.game.result(self.team)


    def assists(self):
        return Assist.objects.filter(goal=self).order_by('order')


    def assist_string(self):
        assists = self.assists()
        if assists:
            return ', '.join([e.player.name for e in assists])
        else:
            return ''
 

    def __str__(self):
        return u"%s: %s (%s)" % (self.game.date, self.player, self.minute)



class Assist(models.Model):
    
    goal = models.ForeignKey(Goal)
    player = models.ForeignKey(Bio)

    # Primary assist (1), secondary assist (2), ad infinitum.
    # Goals and assists could be represented with the same object.
    order = models.IntegerField()

