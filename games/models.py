from collections import defaultdict

from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from places.models import Stadium, City
from sources.models import Source
from teams.models import Team

import random


def pad_list(l, length):
    # Return a list of length length.
    if len(l) >= length:
        return l
    else:
        diff = length - len(l)
        return l + [None] * diff


class GameManager(models.Manager):


    def games(self):
        l = [e['date'] for e in Game.objects.values("date").distinct()]
        return [e for e in l if e is not None]

    def game_years(self):
        return sorted(set([e.year for e in Game.objects.games()]))



    def with_lineups(self):
        from lineups.models import Appearance
        gids = [e[0] for e in set(Appearance.objects.values_list("game"))]
        return Game.objects.filter(id__in=gids)


    def all_blocks(self):
        """
        All date blocks for Beineke +/- analysis.
        """
        l = []
        for g in Game.objects.with_lineups().exclude(date__year=2007):
            print g
            l.extend(g.section_list())
        return l



    def on(self, month, day):
        """
        Return a random game from a given day.
        """
        # Split this into two functions.
        games = Game.objects.filter(date__month=month, date__day=day)
        if games:
            c = games.count()
            i = random.randint(0, c-1)
            return games[i]
        else:
            return None


    def game_dict(self):
        """
        Returns a dict mapping a team/date combination to a game id.
        """
        d = {}
        for e in self.get_query_set():
            key = (e.team1.id, e.date)
            d[key] = e.id
            key2 = (e.team2.id, e.date)
            d[key2] = e.id
        return d

    def team_filter(self, team1, team2=None):
        """
        Return all games played by a given team.
        """

        if team2 is None:
            return Game.objects.filter(models.Q(team1=team1) | models.Q(team2=team1))
        else:
            return Game.objects.filter(models.Q(team1=team1, team2=team2) | models.Q(team2=team1, team1=team2))
            

    def find(self, team, date):
        """
        Given a team name, determine the actual team.
        """
        # Still used? 
        # Should probably do the aliasing in soccerdata

        try:
            game = Game.objects.get(date=date, team1=team)
        except:
            try:
                game = Game.objects.get(date=date, team2=team)
            except:
                game = None

        return game


    def duplicate_games(self):
        """
        Get a list of games where a team plays twice on the same day.
        """
        d = defaultdict(list)
        for e in self.get_query_set():
            k1 = (e.team1, e.date)
            d[k1].append(e)
            k2 = (e.team2, e.date)
            d[k2].append(e)
        return sorted([e for e in  d.values() if len(e) > 1])
            

class Game(models.Model):
    """
    Represents a completed game.
    """
    # Need both a date and a datetime field? Not sure.
    date = models.DateField(null=True)
    
    team1 = models.ForeignKey(Team, related_name='home_games')
    team1_original_name = models.CharField(max_length=255)
    team2 = models.ForeignKey(Team, related_name='away_games')
    team2_original_name = models.CharField(max_length=255)

    team1_score = models.IntegerField(null=True)
    official_team1_score = models.IntegerField(null=True)
    team2_score = models.IntegerField(null=True)    
    official_team2_score = models.IntegerField(null=True)

    team1_result = models.CharField(max_length=5)
    team2_result = models.CharField(max_length=5)

    # Ambiguous game results.
    result_unknown = models.BooleanField(default=False)
    played = models.BooleanField(default=True)

    goals = models.IntegerField()

    # Minigames were played in MLS, APSL, USL, and probably others.
    minigame = models.BooleanField(default=False)

    # Was the game forfeited?
    forfeit = models.BooleanField(default=False)

    minutes = models.IntegerField(default=90)

    # This should probably be a many-to-many?
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)

    # Foreign Key
    stadium = models.ForeignKey(Stadium, null=True)
    city = models.ForeignKey(City, null=True)
    location = models.CharField(max_length=255)

    notes = models.TextField()

    attendance = models.IntegerField(null=True, blank=True)

    referee = models.ForeignKey(Bio, null=True, blank=True, related_name="games_refereed")
    linesman1 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman1_games")
    linesman2 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman2_games")
    linesman3 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman3_games")

    # Detail level of stats.
    # 0 - score only
    # 1 - goals scored and score only
    # 2 - lineups, red cards, etc.
    # 3 - extra data
    detail_level = models.IntegerField(null=True, blank=True)

    # Quality of lineup
    # 0 - no lineups
    # 2 - lineups with logic problems
    # 3 - plausibly complete lineups
    # ? - verified lineup?
    lineup_quality = models.IntegerField(null=True, blank=True)


    source = models.ForeignKey(Source, null=True)
    source_url = models.CharField(max_length=255)

    objects = GameManager()



    class Meta:
        ordering = ('-date',)

        # This no longer seems to be true.
        # unique_together = [('team1', 'date', 'minigame'), ('team2', 'date', 'minigame')]


    
    def winner(self):
        # Need to hook this in more intelligently with team1_result

        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team1_score == self.team2_score:
            return None
        else:
            return self.team2


    def get_completeness(self):
        """Returns how complete a game's data collection is."""
        if self.appearance_set.exists():
            return 2
        elif self.goal_set.exists() or self.team1_score == self.team2_score == 0:
            return 1
        else:
            return 0


    def color_code(self):
        return ['red', 'yellow', 'green'][self.get_completeness()]


    def color_code_result(self):
        return {
            'win': 'green',
            'tie': 'yellow',
            'loss': 'red',
            }[self.result()]


    def score(self):
        """Returns a score string."""
        return "%s - %s" % (self.team1_score, self.team2_score)

    def score_or_result(self):
        """Returns a score string."""
        return "%s - %s" % (self.team1_score_or_result, self.team2_score_or_result)

    @property
    def team1_score_or_result(self):
        if self.team1_score is not None:
            return self.team1_score
        return self.team1_result.capitalize()

    @property
    def team2_score_or_result(self):
        if self.team2_score is not None:
            return self.team2_score
        return self.team2_result.capitalize()



    def team1_lineups(self):
        return self.appearance_set.filter(team=self.team1)



    def team1_starters(self):
        return self.team1_lineups().filter(on=0)


    def team2_starters(self):
        return self.team2_lineups().filter(on=0)

    def lineup_quality(self):
        ts1 = self.team1_starters().count()
        ts2 = self.team2_starters().count()
        if ts1 == 11 and ts2 == 11:
            return 2
        elif ts1 > 0 or ts2 > 0:
            return 1
        else:
            return 0

    def color_code_starters(self):
        # Merge this and color_code
        return ['red', 'yellow', 'green'][self.lineup_quality()]


    def team2_lineups(self):
        return self.appearance_set.filter(team=self.team2)


    def starter_numbers(self):
        """A convenience method for making sure game lineups are good."""
        return "%s:%s" % (self.team1_starters().count(), self.team2_starters().count())



    def zipped_lineups(self):
        # FIX THIS; TRUNACATING TEAM LINEUPS
        t1l, t2l = self.team1_lineups(), self.team2_lineups()
        t1c, t2c = t1l.count(), t2l.count()
        if t1c == t2c:
            return zip(t1l, t2l)
        else:
            m = max(t1c, t2c)
            l1, l2 = pad_list(list(t1l), m), pad_list(list(t2l), m)
            return zip(l1, l2)


    # These should hang off of Team, not Game.
    def previous_games(self, team):
        assert team in (self.team1, self.team2)
        if self.date:
            return Game.objects.team_filter(team).filter(season=self.season).filter(date__lt=self.date).order_by('date')
        else:
            return []

    def streak(self, team):
        """
        Returns a team's results streak, counting this game.
        e.g. 3 wins in a row.
        """

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
        """
        Returns the result of the series between two teams in the same season.
        """
        return Game.objects.filter(season=self.season).filter(
            models.Q(team1=self.team1) | models.Q(team2=self.team1)).filter(
            models.Q(team1=self.team2) | models.Q(team2=self.team2))

        

    def standings(self, team):
        """
        Returns a season's standings as of the current game.
        """
        from collections import defaultdict
        d = defaultdict(int)
        for game in self.previous_games(team):
            d[game.result(team)] += 1
        d[self.result(team)] += 1
        return (d['win'], d['tie'], d['loss'])

    def home_standings(self):
        return self.standings(self.team1)

    def away_standings(self):
        return self.standings(self.team2)

    def home_standings_string(self):
        wins, ties, losses = self.home_standings()
        return "%s-%s-%s" % (wins, ties, losses)

    def away_standings_string(self):
        wins, ties, losses = self.away_standings()
        return "%s-%s-%s" % (wins, ties, losses)


    def streaks(self):
        return [(self.result(e), self.streak(e)) for  e in (self.team1, self.team2)]

    def streak_string(self, t):
        """
        """
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
        """
        Goals for a given team in a given game.
        """
        # Not a great system.
        assert team in (self.team1, self.team2)
        
        if team == self.team1:
            score = self.team1_score
        else:
            score = self.team2_score

        return int(score)


    def goals_against(self, team):
        """
        """
        assert team in (self.team1, self.team2)

        if team == self.team1:
            score = self.team2_score
        else:
            score = self.team1_score

        return int(score)


    def margin(self, team):
        return self.goals_for(team) - self.goals_against(team)



    def result(self, team):
        """
        Returns a string indicating the result of a game
        (win, loss, or tie)
        """
        assert team in (self.team1, self.team2)
        
        try:
            home_score = int(self.official_home_score or self.team1_score)
            away_score = int(self.official_away_score or self.team2_score)
        except:
            return None

        if self.team1_score == self.team2_score: 
            return 'tie'
        if self.team1_score > self.team2_score: 
            if team == self.team1:
                return 'win'
            else:
                return 'loss'
        else:
            if team == self.team1:
                return 'loss'
            else:
                return 'win'



    def same_day_games(self):
        """
        Returns all games played on the same date (excluding this one).
        """
        return Game.objects.filter(date=self.date).exclude(id=self.id)


    def opponent(self, team):
        """
        Given a team, returns the opponent.
        """
        if team == self.team1:
            return self.team2
        elif team == self.team2:
            return self.team1
        else:
            raise




    # Data export/analysis stuff with Beineke.
    
    def game_sections(self):
        # Red cards covered?

        minutes = [int(e[0]) for e in self.appearance_set.all().values_list("on")]
        minutes = sorted(set(minutes))
        minutes_pairs = zip(minutes, minutes[1:]) + [(minutes[-1], 90)]
        return minutes_pairs
        

    
    def goal_blocks(self):

        def add_goal(team, minute):
            for m in sections:
                key = (m, team)
                start_minute, end_minute = m
                if start_minute <= goal_minute < end_minute:
                    goal_dict[key] += 1
                    return
            
            # If a goal doesn't match any time period, add it to the last item.
            # (Presumably the goal was scored in stoppage time)
            goal_dict[key] += 1

        sections = self.game_sections()
        goal_tuples = self.goal_set.all().values_list("team", "minute")
        goal_dict = defaultdict(int)
        for team, goal_minute in goal_tuples:
            add_goal(team, goal_minute)

        return goal_dict
            
        

    def lineup_blocks(self):
        lineup_tuples = self.appearance_set.all().values_list("player", "team", "on", "off")
        sections = self.game_sections()
        d = defaultdict(set)

        for m in sections:
            start_minute, end_minute = m
            for pid, tid, on, off in lineup_tuples:
                number_part = str(pid).zfill(5)
                slug_part = Bio.objects.id_to_slug(pid).zfill(44)
                xid = str("%s:%s" % (number_part, slug_part))

                on, off = int(on), int(off)

                # Handle end of game situations.
                if off != 90:
                    if on <= start_minute and off > start_minute:
                        t = (tid, xid)
                        d[m].add(t)
                else:
                    if on <= start_minute and off >= start_minute:
                        t = (tid, xid)
                        d[m].add(t)

        return d


    def section_list(self):
        """
        All game parts for a given game.
        """
        goal_blocks = self.goal_blocks()
        lineup_blocks = self.lineup_blocks()

        def make_item(section):
            start, end = section

            t1goals = goal_blocks.get((section, self.team1.id), 0)
            t2goals = goal_blocks.get((section, self.team2.id), 0)

            lineups = lineup_blocks[section]

            t1lineups = [e[1] for e in lineups if e[0] == self.team1.id]
            t2lineups = [e[1] for e in lineups if e[0] == self.team2.id]

            return [
                self.id,
                self.date.ctime(),
                start,
                end,
                self.team1.id,
                self.team2.id,
                self.team1.id,
                t1goals,
                t2goals,
                t1lineups,
                t2lineups,
                ]
                
        return [make_item(section) for section in self.game_sections()]





        
    def __unicode__(self):
        return u"%s: %s v %s" % (self.date, self.team1, self.team2)





    def game_scores_by_minute(self):
        """
        Generate a list of dicts representing game scores by minute.
        """
        # How to apply lineups to this?
        # Can't generate anything without goal minutes.
        if self.goals and not self.goal_set.exists():
            pass

        slices = []

        t1_score = t2_score = 0
        t1_goals = defaultdict(int)
        t2_goals = defaultdict(int)


        # Create goal dicts.
        for e in self.goal_set.order_by('minute'):
            if e.team == self.team1:
                t1_goals[e.minute] += 1
            elif e.team == self.team2:
                t2_goals[e.minute] += 1
            else:
                import pdb; pdb.set_trace()
        
        # Create GameMinute objects.
        for minute in range(self.minutes):

            t1_score += t2_goals[minute]
            t2_score += t1_goals[minute]
            

            slices.append({
                    'game_id': self.id,
                    'minute': minute,
                    'team1_score': t1_score,
                    'team2_score': t2_score,
                    })

        return slices







class GameMinute(models.Model):
    """
    Represents a single minute in a single game.
    """
    # The smallest measurable unit in a game.
    # Need to bind a lineup and events to this thing as well.

    game = models.ForeignKey(Game)
    minute = models.IntegerField()
    team1_score = models.IntegerField()
    team2_score = models.IntegerField()


    def goals(self):
        return Goal.objects.filter(game=self.game, minute=self.minute)

    def fouls(self):
        return Foul.objects.filter(game=self.game, minute=self.minute)


    


