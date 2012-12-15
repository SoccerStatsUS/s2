from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from places.models import Stadium
from teams.models import Team



class AbstractStanding(models.Model):
    
    games = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField(null=True)

    # These should probably be pk losses or a more generic term.
    shootout_wins = models.IntegerField(null=True)
    shootout_losses = models.IntegerField(null=True)

    goals_for = models.IntegerField(null=True)
    goals_against = models.IntegerField(null=True)


    class Meta:
        abstract = True

    def goal_ratio(self):
        try:
            return float(self.goals_for) / self.goals_against
        except:
            return 0.0


    def goal_difference(self):
        if self.goals_for and self.goals_against:
            return self.goals_for - self.goals_against
        return None


    def win_percentage(self):
        ties = self.ties or 0
        if self.games:
            return (self.wins + .5 * ties) / self.games
        else:
            return 0

    def win_percentage_100(self):
        return self.win_percentage() * 100



class Standing(AbstractStanding):
    """
    Represents game summary information.
    Usually applied to a team, but could also be a person, competition, season, etc.
    """

    player = models.ForeignKey(Bio, null=True)
    team = models.ForeignKey(Team, null=True)
    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season, null=True)

    # Merge these into one.
    group = models.CharField(max_length=255)
    division = models.CharField(max_length=255)

    # Standing can be a completed standing or just for a given date.
    # Gonna try to generate standings by date.
    final = models.BooleanField(default=True)
    date = models.DateField(null=True)

    points = models.IntegerField(null=True)
    points_deducted = models.IntegerField(null=True)
    deduction_reason = models.TextField()
    position = models.IntegerField(null=True)



    class Meta:
        ordering = ('season', 'competition', '-points', '-wins', 'team')


    def triple(self):
        return "%s-%s-%s" % (self.wins, self.ties, self.losses)


    def __unicode__(self):
        return u"%s %s, %s: %s" % (self.team, self.competition, self.season, self.triple())




    def modern_points(self):
        # 3 for a win, 1 for a tie.
        return self.ties + 3 * self.wins

    def old_points(self):
        return self.ties + 2 * self.wins

    def nasl_points(self):
        # Can't be figured without game data.
        pass



    def round_standings(self, round):
        games = self.game_set.all()[:(round - 1)]
        d = defaultdict(int)
        for game in games:
            result = game.result(self.team)
            d[result] += 1
        return (d['w'], d['t'], d['l'])


    def round_points(self, round):
        wins, ties, losses = self.standings(round)
        return 3 * wins + ties




class StadiumStanding(AbstractStanding):

    team = models.ForeignKey(Team)
    stadium = models.ForeignKey(Stadium)
