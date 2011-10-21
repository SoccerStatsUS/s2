from django.db import models

from s2.teams.models import Team
from s2.competitions.models import Competition, Season


class Standing(models.Model):

    team = models.ForeignKey(Team, null=True)
    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season, null=True)
    division = models.CharField(max_length=255)

    games = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField(null=True)
    points = models.IntegerField(null=True)

    goals_for = models.IntegerField(null=True)
    goals_against = models.IntegerField(null=True)

    shootout_wins = models.IntegerField(null=True)
    shootout_losses = models.IntegerField(null=True)

    class Meta:
        ordering = ('season', 'competition', '-points')


    def triple(self):
        return "%s-%s-%s" % (self.wins, self.ties, self.losses)

    def __unicode__(self):
        return "%s %s, %s: %s" % (self.team, self.competition, self.season, self.triple())


    def win_percentage(self):
        ties = self.ties or 0
        return (self.wins + .5 * ties) / self.games

    def win_percentage_100(self):
        return self.win_percentage() * 100


    def modern_points(self):
        # 3 for a win, 1 for a tie.
        return self.ties + 3 * self.wins

    def old_points(self):
        return self.ties + 2 * self.wins

    def nasl_points(self):
        # Can't be figured without game data.
        pass


