from collections import defaultdict

from django.db import models

from s2.teams.models import Team
from s2.competitions.models import Competition, Season

import random


class GameManager(models.Manager):

    def on(self, month, day):
        games = Game.objects.filter(date__month=month, date__day=day)
        if games:
            c = games.count()
            i = random.randint(0, c-1)
            return games[i]
        else:
            return None


    def game_dict(self):
        d = {}
        for e in self.get_query_set():
            key = (e.home_team.id, e.date)
            d[key] = e.id
            key2 = (e.away_team.id, e.date)
            d[key2] = e.id
        return d

    def team_filter(self, team):
        return Game.objects.filter(models.Q(home_team=team) | models.Q(away_team=team))
            

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
    official_home_score = models.IntegerField(null=True)

    away_team = models.ForeignKey(Team, related_name='away_games')
    away_score = models.IntegerField()
    official_away_score = models.IntegerField(null=True)

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


    # These should hang off of Team, not Game.
    def previous_games(self, team):
        assert team in (self.home_team, self.away_team)
        return Game.objects.team_filter(team).filter(season=self.season).filter(date__lt=self.date).order_by('date')

    def streak(self, team):

        result = self.result(team)
        s = 1

        games = self.previous_games(team).order_by('-date')
        for e in games:
            r = e.result(team)
            if r != result:
                return s
            else:
                s += 1

        return s

    def series(self):
        return Game.objects.filter(season=self.season).filter(
            models.Q(home_team=self.home_team) | models.Q(away_team=self.home_team)).filter(
            models.Q(home_team=self.away_team) | models.Q(away_team=self.away_team))

        

    def standings(self, team):
        from collections import defaultdict
        d = defaultdict(int)
        for game in self.previous_games(team):
            d[game.result(team)] += 1
        d[self.result(team)] += 1
        return (d['win'], d['tie'], d['loss'])

    def home_standings(self):
        return self.standings(self.home_team)

    def home_standings_string(self):
        wins, ties, losses = self.home_standings()
        return "%s-%s-%s" % (wins, ties, losses)


    def away_standings(self):
        return self.standings(self.away_team)

    def away_standings_string(self):
        wins, ties, losses = self.away_standings()
        return "%s-%s-%s" % (wins, ties, losses)

        

    def streaks(self):
        return [(self.result(e), self.streak(e)) for  e in (self.home_team, self.away_team)]

    def streak_string(self, t):
        d = {
            'tie': 'ties',
            'loss': 'losses',
            'win': 'wins',
            }
        stype, count = t
        if count != 1:
            stype = d[stype]
        return "%s %s" % (count, stype)

    def home_streak_string(self):
        return self.streak_string(self.streaks()[0])
    
    def away_streak_string(self):
        return self.streak_string(self.streaks()[1])

    def goals_for(self, team):
        assert team in (self.home_team, self.away_team)
        
        if team == self.home_team:
            score = self.home_score
        else:
            score = self.away_score

        return int(score)


    def goals_against(self, team):
        assert team in (self.home_team, self.away_team)

        if team == self.home_team:
            score = self.away_score
        else:
            score = self.home_score

        return int(score)

        


    def result(self, team):
        assert team in (self.home_team, self.away_team)
        
        try:
            home_score = int(self.official_home_score or self.home_score)
            away_score = int(self.official_away_score or self.away_score)
        except:
            return None

        if home_score == away_score:
            return 'tie'
        if home_score > away_score:
            if team == self.home_team:
                return 'win'
            else:
                return 'loss'
        else:
            if team == self.home_team:
                return 'loss'
            else:
                return 'win'


    def same_day_games(self):
        return Game.objects.filter(date=self.date).exclude(id=self.id)



        

        
        


    def __unicode__(self):
        return u"%s: %s v %s" % (self.date, self.home_team, self.away_team)

    def opponent(self, team):
        if team == self.home_team:
            return self.away_team
        elif team == self.away_team:
            return self.home_team
        else:
            raise



