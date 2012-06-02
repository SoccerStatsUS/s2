from django.db import models

from bios.models import Bio
from goals.models import Goal
from games.models import Game, GameMinute
from teams.models import Team

from django.db.models.signals import post_save


class Appearance(models.Model):

    player = models.ForeignKey(Bio)

    team = models.ForeignKey(Team)
    team_original_name = models.CharField(max_length=255)
    
    game = models.ForeignKey(Game)

    on = models.IntegerField(null=True)
    off = models.IntegerField(null=True)
    
    # Default should be integer.


    age = models.FloatField(null=True) # Age in years at the time of game.

    class Meta:
        ordering = ('game', 'on', '-id' )


    def opponent(self):
        if self.team == self.game.team1:
            return self.game.team2
        else:
            return self.game.team1

    
    @property
    def minutes(self):
        try:
            return int(self.off) - int(self.on)
        except:
            return None


    @property
    def goals(self):
        Goal.objects.filter(player=self.player, game=self.game).count()


    @property
    def assists(self):
        return None

    @property
    def result(self):
        return self.game.result(self.team)


    @property
    def goals_for(self):
        team_goals = Goal.objects.filter(game=self.game, team=self.team, minute__gte=self.on, minute__lte=self.off).count()
        return team_goals

    @property
    def goals_against(self):
        opponent = self.game.opponent(self.team)
        opponent_goals = Goal.objects.filter(game=self.game, team=opponent, minute__gte=self.on, minute__lte=self.off).count()
        return opponent_goals


    @property
    def goal_differential(self):
        try:
            return self.goals_for - self.goals_against
        except:
            return None



    
def set_appearance_age(sender, instance, created, **kwargs):
    if not instance.age and instance.player.birthdate:
        instance.age = (instance.game.date - instance.player.birthdate).days
        try:
            instance.save()
        except:
            import pdb; pdb.set_trace()
            x=5
            

post_save.connect(set_appearance_age, sender=Appearance)


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
    
