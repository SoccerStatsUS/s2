from collections import defaultdict

from django.db import models

from s2.teams.models import Team
from s2.competitions.models import Competition, Season


class GameManager(models.Manager):

    def game_dict(self):
        d = {}
        for e in self.get_query_set():
            key = (e.home_team.id, e.date)
            d[key] = e.id
            key2 = (e.away_team.id, e.date)
            d[key2] = e.id
        return d


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


    def duplicate_games(self):
        """
        Get a list of games where a team plays twice on the same day.
        """
        d = defaultdict(list)
        for e in self.get_query_set():
            k1 = (e.home_team, e.date)
            d[k1].append(e)
            k2 = (e.away_team, e.date)
            d[k2].append(e)
        return sorted([e for e in  d.values() if len(e) > 1])

            

class Game(models.Model):
    """
    Represents a completed game.
    """
    # Redesign this so that we don't have a home team home score situation?

    # Should we have a date and a datetime field?
    date = models.DateField()
    
    home_team = models.ForeignKey(Team, related_name='home_games')
    home_score = models.IntegerField()

    away_team = models.ForeignKey(Team, related_name='away_games')
    away_score = models.IntegerField()

    # This should probably be a many-to-many?
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)

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



