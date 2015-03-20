from django.db import models

from s2.bios.models import Bio
from s2.goals.models import Goal
from s2.games.models import Game, GameMinute
from s2.teams.models import Team

from django.db.models.signals import post_save


class Appearance(models.Model):

    player = models.ForeignKey(Bio)

    team = models.ForeignKey(Team)
    #opponent = models.ForeignKey(Team)
    
    game = models.ForeignKey(Game)

    # What order the player is the lineup. (Matt Reis, Avery John, Michael Parkhurst) -> Michael Parkhurst, 3
    order = models.IntegerField(null=True)

    on = models.IntegerField(null=True)
    off = models.IntegerField(null=True)

    #result = models.CharField(max_length=5)
    #goals_for = models.IntegerField(null=True)
    #goals_against = models.IntegerField(null=True)

    # Default should be integer.

    #age = models.FloatField(null=True) # Age in years at the time of game.
    minutes = models.IntegerField(null=True)

    class Meta:
        ordering = ('game', 'order', 'on', '-id' )
        pass

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



    @property
    def goals(self):
        Goal.objects.filter(player=self.player, game=self.game).count()


    @property
    def assists(self):
        return None

    def score_or_result(self):
        if self.team == self.game.team1:
            return self.game.score_or_result()
        else:
            return self.game.reverse_score_or_result()

    @property
    def goal_differential(self):
        try:
            return self.goals_for - self.goals_against
        except:
            return None


"""
It's possible that we're reaching the point where we should denormalize things and create the different redis stuff.
Keep the regular database as simple as possible and build the abstractions as extensions?
"""


class AppearanceMinute(object):
    """
    Reresents a single minute that a player played.
    What happened during this minute?
    Any cool events?
    """

    #appearance = models.ForeignKey(Appearance)
    #gameMinute = models.ForeignKey(GameMinute)
    #minute = models.IntegerField()
    
