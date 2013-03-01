from collections import defaultdict
import datetime
import math
import random


from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from places.models import Stadium, City
from sources.models import Source
from teams.models import Team



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


    # Secondary data.
    round = models.CharField(max_length=255)


    starter_count = models.IntegerField(null=True, blank=True)
    goal_count = models.IntegerField(null=True, blank=True)

    date = models.DateField(null=True)
    has_date = models.BooleanField()
    
    team1 = models.ForeignKey(Team, related_name='t1_games')
    team1_original_name = models.CharField(max_length=255)
    team2 = models.ForeignKey(Team, related_name='t2_games')
    team2_original_name = models.CharField(max_length=255)

    team1_score = models.IntegerField(null=True)
    official_team1_score = models.IntegerField(null=True)
    team2_score = models.IntegerField(null=True)    
    official_team2_score = models.IntegerField(null=True)

    team1_result = models.CharField(max_length=5)
    team2_result = models.CharField(max_length=5)

    shootout_winner = models.ForeignKey(Team, null=True, related_name='something')
    #some_field = models.IntegerField(null=True)    


    # Ambiguous game results.
    result_unknown = models.BooleanField(default=False)
    played = models.BooleanField(default=True)
    # Was the game forfeited?
    forfeit = models.BooleanField(default=False)

    # Goals scored in the game.
    goals = models.IntegerField()

    # Minigames were played in MLS, APSL, USL, and probably others.
    minigame = models.BooleanField(default=False)

    minutes = models.IntegerField(default=90)

    # This should probably be a many-to-many?
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)

    home_team = models.ForeignKey(Team, null=True, related_name='home_games')
    neutral = models.BooleanField(default=False)

    stadium = models.ForeignKey(Stadium, null=True)
    city = models.ForeignKey(City, null=True)
    location = models.CharField(max_length=255)

    notes = models.TextField()

    attendance = models.IntegerField(null=True, blank=True)

    referee = models.ForeignKey(Bio, null=True, blank=True, related_name="games_refereed")
    linesman1 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman1_games")
    linesman2 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman2_games")
    linesman3 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman3_games")

    sources = models.ManyToManyField(Source, through='GameSource')

    objects = GameManager()



    class Meta:
        ordering = ('-date',)

        # This no longer seems to be true.
        # unique_together = [('team1', 'date', 'minigame'), ('team2', 'date', 'minigame')]


    def team1_previous_game(self):
        return self.team1.previous_game(self)

    def team1_next_game(self):
        return self.team1.next_game(self)

    def team2_previous_game(self):
        return self.team2.previous_game(self)

    def team2_next_game(self):
        return self.team2.next_game(self)


    def away_team(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team2
        else:
            return self.team1


    def home_score(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team1_score
        else:
            return self.team2_score


    def away_score(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team2_score
        else:
            return self.team1_score

    
    def winner(self):
        # Need to hook this in more intelligently with team1_result

        if self.shootout_winner:
            return self.shootout_winner

        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team1_score == self.team2_score:
            return None
        else:
            return self.team2


    def get_completeness(self):
        """Returns how complete a game's data collection is."""
        if self.starter_count == 22:
            return 2
        elif self.starter_count == 0 and self.goal_count == 0:
            return 0
        return 1


    def color_code(self):
        return ['red', 'yellow', 'green'][self.get_completeness()]


    def color_code_result(self):
        return {
            'win': 'green',
            'tie': 'yellow',
            'loss': 'red',
            }[self.result()]

    def lineup_color_code(self):
        # Merge this and color_code
        return ['red', 'yellow', 'green'][self.lineup_quality()]

    def goal_color_code(self):
        # Merge this and color_code
        return ['red', 'yellow', 'green'][self.goal_quality()]





    def score(self):
        """Returns a score string."""
        return "%s - %s" % (self.team1_score, self.team2_score)

    def score_or_result_generic(self, func):
        """Returns a score string."""
        if self.date is not None and self.date > datetime.date.today():
            return 'v'

        if self.result_unknown:
            return '?'

        elif self.team1_result == self.team2_result == '':
            return 'np'
        else:
            return func()


    def result_string(self):
        s = "%s - %s" % (self.team1_score_or_result, self.team2_score_or_result)
        return s

    def score_or_result(self):
        return self.score_or_result_generic(self.result_string)

    def reverse_result_string(self):
        return "%s - %s" % (self.team2_score_or_result, self.team1_score_or_result)

    def reverse_score_or_result(self):
        return self.score_or_result_generic(self.reverse_result_string)


    @property
    def team1_score_or_result(self):
        if self.team1_score is not None:
            if self.shootout_winner == self.team1:
                return "(SOW) %s" % self.team1_score
            else:
                return self.team1_score
        return self.team1_result.capitalize()

    @property
    def team2_score_or_result(self):
        if self.team2_score is not None:
            if self.shootout_winner == self.team2:
                return "%s (SOW)" % self.team2_score
            else:
                return self.team2_score
        return self.team2_result.capitalize()


    def team1_lineups(self):
        return self.appearance_set.filter(team=self.team1)

    def team2_lineups(self):
        return self.appearance_set.filter(team=self.team2)

    def team1_starters(self):
        return self.team1_lineups().filter(on=0).exclude(off=0)


    def team2_starters(self):
        return self.team2_lineups().filter(on=0).exclude(off=0)

    def lineup_quality(self):
        if self.starter_count == 22:
            return 2
        elif self.starter_count > 0:
            return 1
        return 0


    def goal_quality(self):

        if self.team1_score is None or self.team2_score is None:
            return 0

        score_goals = self.team1_score + self.team2_score
        if self.goal_count == score_goals:
            return 2
        elif self.goal_count > 0:
            return 1
        else:
            return 0


    def starter_numbers(self):
        """A convenience method for making sure game lineups are good."""
        return "%s:%s" % (self.team1_starter_count, self.team2_starter_count)



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
        from standings.models import Standing
        try:
            return Standing.objects.get(date=self.date, season=self.season, team=self.team1)
        except:
            return None

    def away_standings(self):
        from standings.models import Standing
        try:
            return Standing.objects.get(date=self.date, season=self.season, team=self.team2)
        except:
            return None

    def home_standings_string(self):
        s = self.home_standings()
        if s:
            return "%s-%s-%s" % (s.wins, s.ties, s.losses)
        else:
            return ''

    def away_standings_string(self):
        s = self.away_standings()
        if s:
            return "%s-%s-%s" % (s.wins, s.ties, s.losses)
        else:
            return ''

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
            team1_score = int(self.official_team1_score or self.team1_score)
            team2_score = int(self.official_team2_score or self.team2_score)
        except:
            return None

        if team1_score == team2_score: 
            return 't'
        if team1_score > team2_score: 
            if team == self.team1:
                return 'w'
            else:
                return 'l'
        else:
            if team == self.team1:
                return 'l'
            else:
                return 'w'

        raise



    def same_day_games(self):
        """
        Returns all games played on the same date (excluding this one).
        """
        if self.date:
            return Game.objects.filter(date=self.date).exclude(id=self.id).order_by('competition__level', 'competition__name')
        else:
            return []


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

        no_minute_goals = self.goal_set.filter(minute=None)
        if no_minute_goals.exists():
            return []

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



def get_best_game_ids():
    competitions = Competition.objects.filter(slug__in=['major-league-soccer', 'usl-first-division', 'usl-second-division', 'ussf-division-2-professional-league', 'north-american-soccer-league-2011-'])
    competitions = Competition.objects.filter(slug__in=['major-league-soccer'])
    games = Game.objects.filter(competition__in=competitions).filter(date__gte=datetime.date(2004, 1, 1)).filter(date__lt=datetime.date(2012, 1, 1))
    
    gids = []
    #import pdb; pdb.set_trace()
    for gid, t1s, t2s, gc in games.filter(starter_count=22).values_list('id', 'team1_score', 'team2_score', 'goal_count'):
        if t1s + t2s == gc:
            gids.append(gid)

    #import pdb; pdb.set_trace()
            

    print "Using %s out of %s games" % (len(gids), games.count())

    return gids
        

def make_game_blocks():
    l = []
    gids = get_best_game_ids()
    games = Game.objects.filter(id__in=gids)

    used = 0

    for game in games:
        slices = game.game_scores_by_minute()
        l.extend(slices)
        if len(slices) > 0:
            used += 1

    print "%s out of %s games with complete data" % (len(gids), used)

    return l




class GameSource(models.Model):
    """
    A many-to-many mapping of a source to a single game.
    """
    # A separate model is used to include source_url, which is unique to each mapping.


    game = models.ForeignKey(Game)
    source = models.ForeignKey(Source)
    source_url = models.CharField(max_length=1023)



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


    

def calculate_team_scores(qs):
    # Based on http://dev.soccerstats.us/static/docs/predicting-soccer-matches.pdf
    
    team_game_dates = defaultdict(list)
    team_attack_ratings = defaultdict(list)
    team_defense_ratings = defaultdict(list)


    # xA,B = number of goals scored for team A against team B
    # Delta-a-b = (attack-a + defense-a - attack-b - defense-b) / 2
    # Goals will be poisson-distributed with the distribution equal to
    # xAB = log-home-goals + attack-a - defense-b - psychology * delta-a-b

    # Rue and Salvesen adjust the poisson-distribution to increase the probability of 0-0 and 1-1
    # results at the cost of 0-1 and 1-0 results. Apparently due to empirical observation? (Dixon and Coles (1997))
    # home and away scores are not independend of each other.
    
    # Furthermore, they truncate all scores at 5 goals.



    home_goal_log, away_goal_log = get_score_constants(l)

    # These were picked by Rue and Salvesen to optimize their model's success at making predictions.
    # Adopting them verbatim now until I can run a similar test.
    memory_length = 100 # tau

    # gamma; adjusts for stronger teams underestimating weaker ones. a negative gamma would indicate that stronger teams
    # would psychologically overwhelm weaker ones. Potentially true in the case of large team ability mismatches.
    psychological_constant = .1 

    # Estimate of the randomness of a match result. (1-epsilon) * 100% of the "information" in the match is informative regarding
    # team strengths, the resulting epsilon information is non-informative.
    epsilon = .2 # epsilon


    l = qs.exclude(date=None).order_by('date')

    for game in l:
        team_game_dates[game.team1].append(game.date)
        team_game_dates[game.team2].append(game.date)

    

def sample_attack(current_value, global_distribution):
    # Sample a value from a gaussian distribution. Return it with the acceptance probability, otherwise
    # keep the old value.
    sample = math.gauss(current_balue, global_distribution)

    acceptance_probability = None # Quite confusing.
    if acceptance_probability > random.random():
        return sample
    else:
        return None


def brownian_team_strength(previous_values, tnew, told):
    brownian_motion = (simple_brownian(float(tnew)/memory_length) - simple_brownian(float(tnew)/memory_length))

    divisor = math.sqrt(1 - psychological_constant * (1 - psychological_constant / 2))
    prior_variance = numpy.var(previous_values)
    dividend = math.sqrt(prior_variance) # sigmaA^2 = the prior variance for aA.
    new_strength = previous_strength + ((brownian_motion * dividend) / divisor)
    pass




def estimate_match_result(match):
    # Trying to implement move type 2.
    # Basically, estimate the result of a match based on team strengths.

    if random.random() < epsilon:
        lambda_x = global_home_score
        lambda_y = global_away_score
    else:
        lambda_x = old_lambda_x
        lambda_y = old_lambda_y

    while True:
        # Draw x from lambda x (some distribution of x scores) until x <= 5.
        # Do the same for y.
        # if x and y are within some weird probablility paramters, set x and y to the appropriate values.
        # Otherwise, keep pulling values.
        return None, None

    


def get_home_bias(qs):
    home_scores = away_scores = 0
    for t1, t1s, t2, t2s, ht in qs.values_list('team1', 'team1_score', 'team2', 'team2_score', 'home_team'):
        if t1 == ht:
            home_scores += t1s
            away_scores += t2s
        elif t2 == ht:
            home_scores += t2s
            away_scores += t1s

        else:
            import pdb; pdb.set_trace()

    return (home_scores, away_scores, qs.count())



def get_score_constants(qs):
    home, away, count = get_home_bias(qs)
    home_log = math.log(float(home)/count)
    away_log = math.log(float(away)/count)
    return home_log, away_log
        


def simple_brownian(f):
    return brownian(f, 1, 1, 1)


"""
brownian() implements one dimensional Brownian motion (i.e. the Wiener process).
"""

# File: brownian.py

from math import sqrt
from scipy.stats import norm
import numpy as np


def brownian(x0, n, dt, delta, out=None):
    # From http://www.scipy.org/Cookbook/BrownianMotion
    """\
    Generate an instance of Brownian motion (i.e. the Wiener process):

        X(t) = X(0) + N(0, delta**2 * t; 0, t)

    where N(a,b; t0, t1) is a normally distributed random variable with mean a and
    variance b.  The parameters t0 and t1 make explicit the statistical
    independence of N on different time intervals; that is, if [t0, t1) and
    [t2, t3) are disjoint intervals, then N(a, b; t0, t1) and N(a, b; t2, t3)
    are independent.
    
    Written as an iteration scheme,

        X(t + dt) = X(t) + N(0, delta**2 * dt; t, t+dt)


    If `x0` is an array (or array-like), each value in `x0` is treated as
    an initial condition, and the value returned is a numpy array with one
    more dimension than `x0`.

    Arguments
    ---------
    x0 : float or numpy array (or something that can be converted to a numpy array
         using numpy.asarray(x0)).
        The initial condition(s) (i.e. position(s)) of the Brownian motion.
    n : int
        The number of steps to take.
    dt : float
        The time step.
    delta : float
        delta determines the "speed" of the Brownian motion.  The random variable
        of the position at time t, X(t), has a normal distribution whose mean is
        the position at time t=0 and whose variance is delta**2*t.
    out : numpy array or None
        If `out` is not None, it specifies the array in which to put the
        result.  If `out` is None, a new numpy array is created and returned.

    Returns
    -------
    A numpy array of floats with shape `x0.shape + (n,)`.
    
    Note that the initial value `x0` is not included in the returned array.
    """

    x0 = np.asarray(x0)

    # For each element of x0, generate a sample of n numbers from a
    # normal distribution.
    r = norm.rvs(size=x0.shape + (n,), scale=delta*sqrt(dt))

    # If `out` was not given, create an output array.
    if out is None:
        out = np.empty(r.shape)

    # This computes the Brownian motion by forming the cumulative sum of
    # the random samples. 
    np.cumsum(r, axis=-1, out=out)

    # Add the initial condition.
    out += np.expand_dims(x0, axis=-1)

    return out
