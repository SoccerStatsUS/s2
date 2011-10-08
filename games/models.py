from django.db import models

from s2.teams.models import Team

class GameManager(models.Manager):

    def find(self, team, date):
        """
        Given a team name, determine the actual team.
        """

        try:
            game = Game.objects.get(date=date, home_team=team)
        except:
            try:
                game = Game.objects.get(date=date, away_team=team)
            except:
                game = None

        return game
            

class Game(models.Model):
    """
    Represents a completed game.
    """
    # Should we have a date and a datetime field?
    date = models.DateField()
    
    home_team = models.ForeignKey(Team, related_name='home_games')
    home_score = models.IntegerField()

    away_team = models.ForeignKey(Team, related_name='away_games')
    away_score = models.IntegerField()

    # This should probably be a many-to-many?
    competition = models.CharField(max_length=255)
    season = models.CharField(max_length=255)

    location = models.CharField(max_length=255)

    notes = models.TextField()

    attendance = models.IntegerField(null=True, blank=True)
    referee = models.CharField(max_length=255)

    objects = GameManager()


    class Meta:
        ordering = ('-date',)
        unique_together = [('home_team', 'date'), ('away_team', 'date')]


    def score(self):
        return "%s - %s" % (self.home_score, self.away_score)


    def __unicode__(self):
        return u"%s: %s v %s" % (self.date, self.home_team, self.away_team)



