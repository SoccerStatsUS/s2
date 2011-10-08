from django.db import models

from s2.teams.models import Team
from s2.competitions.models import Competition, Season


class Standing(models.Model):

    team = models.ForeignKey(Team)
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)

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


