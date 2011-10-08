from django.db import models

from s2.teams.models import Team


class Standing(models.Model):

    team = models.ForeignKey(Team)
    competition = models.CharField(max_length=255)
    season = models.CharField(max_length=255)

    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField()
    points = models.IntegerField()

    goals_for = models.IntegerField()
    goals_against = models.IntegerField()

    class Meta:
        ordering = ('season', 'competition', '-points')


    def triple(self):
        return "%s-%s-%s" % (self.wins, self.ties, self.losses)

    def __unicode__(self):
        return "%s %s, %s: %s" % (self.team, self.competition, self.season, self.triple())


