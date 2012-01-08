from django.db import models

from s2.bios.models import Bio
from s2.goals.models import Goal
from s2.games.models import Game
from s2.teams.models import Team

from django.db.models.signals import post_save


class Appearance(models.Model):

    player = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)
    game = models.ForeignKey(Game)

    #on = models.IntegerField()
    #off = models.IntegerField()
    
    # Default should be integer.
    on = models.CharField(max_length=255)
    off = models.CharField(max_length=255)

    age = models.IntegerField(null=True) # Number of days since birth.

    class Meta:
        ordering = ('game', )



    def opponent(self):
        if self.team == self.game.home_team:
            return self.game.away_team
        else:
            return self.game.home_team

    
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
        return self.goals_for - self.goals_against

    def pretty_age(self):
        return self.age / 365.25


    
def set_appearance_age(sender, instance, created, **kwargs):
    if not instance.age and instance.player.birthdate:
        instance.age = (instance.game.date - instance.player.birthdate).days
        try:
            instance.save()
        except:
            import pdb; pdb.set_trace()
            x=5
            

post_save.connect(set_appearance_age, sender=Appearance)
