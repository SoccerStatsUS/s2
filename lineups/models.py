from django.db import models

from s2.bios.models import Bio
from s2.goals.models import Goal
from s2.games.models import Game
from s2.teams.models import Team

class Appearance(models.Model):

    player = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)
    game = models.ForeignKey(Game)

    #on = models.IntegerField()
    #off = models.IntegerField()
    
    # Default should be integer.
    on = models.CharField(max_length=255)
    off = models.CharField(max_length=255)

    class Meta:
        ordering = ('game', )

    @property
    def age(self):
        if self.player.bio.birthdate:
            return self.date - self.player.bio.birthdate


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


        
