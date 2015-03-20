from django.db.models import Sum, Avg
from django.db import models
from django.template.defaultfilters import slugify

from collections import defaultdict

from s2.bios.models import Bio


import datetime




def nationality_stats(stats):
    from collections import Counter
    from places.models import Country

    # In the process of Creating a more generic state/country/confederation key part.
    # Need to creat Confederation...
    

    
    stats = stats.exclude(player__birthplace__country=None)
    
    minutes_dict = defaultdict(int)
    gp_dict = defaultdict(int)
    
    nationality_set = set()

    for nat, pid, gp, minutes in stats.values_list('player__birthplace__country', 'player', 'games_played', 'minutes'):
        nationality_set.add((pid, nat))
        minutes_dict[nat] += minutes or 0
        gp_dict[nat] += gp or 0

    nation_count = Counter([e[1] for e in nationality_set])

    total_count = sum(nation_count.values())
    total_minutes = sum(minutes_dict.values())
    total_gp = sum(gp_dict.values())


    l = []

    nationality_ids = set([e[1] for e in nationality_set])        

    nx = Country.objects.filter(id__in=nationality_ids)
    nation_dict = dict([(e.id, e) for e in nx])

    for n in nationality_ids:
        nation = nation_dict[n]
        uniques = nation_count[n]

        minutes = minutes_dict[n]

        gp = gp_dict[n]
        if total_gp:
            gp_percentage = 100 * gp / float(total_gp)
            gp_per_person = gp / float(uniques)
        else:
            gp_percentage = None
            gp_per_person = None



        l.append((nation, uniques, gp, gp_percentage, minutes, gp_per_person))

    l = sorted(l, key=lambda e: -e[2])
    return {
        'total_minutes': total_minutes,
        'total_gp': total_gp,
        'total_count': total_count,
        'stat_list': l,
        }
            

def confederation_stats(stats):
    from collections import Counter
    # Ha. Rebuilt this entirely.

    # In the process of Creating a more generic state/country/confederation key part.
    # Need to creat Confederation...
    
    stats = stats.exclude(player__birthplace__country=None)
    
    minutes_dict = defaultdict(int)
    gp_dict = defaultdict(int)
    
    nationality_set = set()

    for nat, pid, gp, minutes in stats.values_list('player__birthplace__country__confederation', 'player', 'games_played', 'minutes'):
        nationality_set.add((pid, nat))
        minutes_dict[nat] += minutes or 0
        gp_dict[nat] += gp or 0


    nation_count = Counter([e[1] for e in nationality_set])

    total_count = sum(nation_count.values())
    total_minutes = sum(minutes_dict.values())
    total_gp = sum(gp_dict.values())



    l = []

    confederations = set([e[1] for e in nationality_set])        

    #nx = Country.objects.filter(id__in=nationality_ids)
    #nation_dict = dict([(e.id, e) for e in nx])

    for n in confederations:
        #nation = nation_dict[n]
        uniques = nation_count[n]
        unique_percentage = 100 * uniques / float(total_count)


        minutes = minutes_dict[n]

        gp = gp_dict[n]

        gp = gp_dict[n]
        if total_gp:
            gp_percentage = 100 * gp / float(total_gp)
            gp_per_person = gp / float(uniques)
        else:
            gp_percentage = None
            gp_per_person = None


        l.append((n, uniques, gp, gp_percentage, minutes, gp_per_person))

    l = sorted(l, key=lambda e: -e[2])

    return {
        'total_minutes': total_minutes,
        'total_gp': total_gp,
        'total_count': total_count,
        'stat_list': l,
        }


class Code(models.Model):
    """
    A soccer code
    eg soccer, indoor, women's...
    """
    name = models.CharField(max_length=255)
            


class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            print("Creating competition {}".format(name))
            return Competition.objects.create(name=name)


    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d


class AbstractCompetition(models.Model):

    # Anything that has a standing_set and a game_set 
    # mostly competitions and seasons.


    def standings_games(self):
        return sum(self.standing_set.filter(final=True).values_list('games', flat=True)) / 2

    def known_games(self):
        return self.game_set.exclude(team1_result='').count()

    def max_games(self):
        return max([self.standings_games(), self.known_games()])

    def min_games(self):
        return min([self.standings_games(), self.known_games()])

    def verified_games(self):
        gg = self.known_games()
        sg = self.standings_games()

        if sg == 0:
            return 0
        elif sg == gg:
            return None
        else:
            return gg / float(sg)



    def attendance_games(self):
        gg = self.game_set.exclude(attendance=None).count()
        sg = self.standings_games()

        if sg == 0:
            return 0
        elif sg == gg:
            return None
        else:
            return gg / float(sg)



    def total_attendance(self):
        games = self.game_set.exclude(attendance=None)
        return games.aggregate(Sum('attendance'))['attendance__sum']
        
    def average_attendance(self):
        games = self.game_set.exclude(attendance=None)
        if games.exists():
            return int(games.aggregate(Avg('attendance'))['attendance__avg'])
        else:
            return None

    class Meta:
        abstract = True


    




class Competition(AbstractCompetition):
    """
    A generic competition such as MLS Cup Playoffs, US Open Cup, or Friendly
    """
    # Should this be called Tournament? Probably not.

    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=15)
    
    slug = models.SlugField(max_length=150)

    international = models.BooleanField(default=False)
    ctype = models.CharField(max_length=255) # Competition type - cup, league, etc.
    code = models.CharField(max_length=255) # Code: soccer, indoor, Boston game, etc.
    level = models.IntegerField(null=True, blank=True) # 1st Divison, 2nd Vision, etc.
    scope = models.CharField(max_length=255)

    area = models.CharField(max_length=255)

    relationships = models.ManyToManyField('self',through='CompetitionRelationship',symmetrical=False)

    
    #international = models.BooleanField()

    objects = CompetitionManager()

    class Meta:
        ordering = ("name",)


    def __unicode__(self):
        return self.name

    def make_abbreviation(self):
        
        if self.name is None:
            import pdb; pdb.set_trace()

        words = self.name.split(' ')
        first_letters = [e.strip()[0] for e in words if e.strip()]
        first_letters = [e for e in first_letters if e not in '-()']
        return "".join(first_letters)


    def color_code(self):
        if self.ctype == 'Cup':
            return 'orange'
        elif self.ctype == 'League':
            if self.level == 1:
                return 'blue'
            else:
                return 'light-blue'
        elif self.name == 'Friendly':
            return 'light-grey'
        else:
            return ''


    def has_mvp(self):
        from awards.models import Award
        return Award.objects.filter(competition=self, type='mvp').exists()


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.abbreviation:
            self.abbreviation = self.make_abbreviation()
            
        super(Competition, self).save(*args, **kwargs)


    def category(self):
        if self.international:
            return "international"
        
        elif self.ctype == '':
            return "friendly"

        else:
            return "domestic"


    def alltime_standings(self):
        from standings.models import Standing
        return Standing.objects.filter(competition=self, season=None)

    def first_alltime_standing(self):
        return self.alltime_standings()[0]

    def first_season(self):

        if self.season_set.exists():
            return self.season_set.all()[0]
        else:
            return None

    def last_season(self):
        seasons = self.season_set.count()
        if seasons:
            index = seasons - 1
            return self.season_set.all()[index]
        else:
            return None


    def nationality_stats(self):
        from stats.models import CompetitionStat
        stats = CompetitionStat.objects.filter(competition=self)
        return nationality_stats(stats)

    def confederation_stats(self):
        from stats.models import CompetitionStat
        stats = CompetitionStat.objects.filter(competition=self)
        return confederation_stats(stats)



class CompetitionRelationship(models.Model):
    before = models.ForeignKey('Competition', related_name='before')
    after = models.ForeignKey('Competition', related_name='after')




class SeasonManager(models.Manager):

    def find(self, name, competition):
        try:
            return Season.objects.get(name=name, competition=competition)
        except:
            #if type(competition) in (int, str, unicode):
            if type(competition) in (int, str):
                competition = Competition.objects.get(id=competition)
            
            try:
                ss = SuperSeason.objects.get(name=name)
            except:
                print("Creating Super Season %s" % name)
                if name in (None, ''):
                    import pdb; pdb.set_trace()
                ss = SuperSeason.objects.create(name=name, order=-1, order2=-1)

            return Season.objects.create(name=name, competition=competition, order=ss.order, super_season=ss)

    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for name, competition, sid in self.get_query_set().values_list('name', 'competition', 'id'):
            d[(name, competition)] = sid
        return d



    def as_dictold(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_query_set():
            if e.competition:
                d[(e.name, e.competition.id)] = e.id
            else:
                d[(e.name, None)] = e.id
        return d



class SuperSeason(models.Model):
    """
    A larger version of season.
    eg 1996, 2004-2005
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    order = models.IntegerField()
    order2 = models.IntegerField()


    
    def previous(self):
        seasons = SuperSeason.objects.all()
        index = list(seasons).index(self)
        if index > 0:
            return seasons[index - 1]
        else:
            return None

    def next(self):
        seasons = SuperSeason.objects.all()
        index = list(seasons).index(self)
        next = index + 1
        if next < seasons.count():
            return seasons[next]
        else:
            return None




class Season(AbstractCompetition):
    """
    A season of a competition.
    """
    # Considering removing the competition dependency and making season refer to a given period of time.
    # A CompetitionSeason would then refer to a season/competition unit.

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    order = models.IntegerField(null=True, blank=True)
    order2 = models.IntegerField(null=True, blank=True)

    competition = models.ForeignKey(Competition, null=True)
    competition_original_name = models.CharField(max_length=255)

    objects = SeasonManager()

    minutes = models.IntegerField(null=True, blank=True)
    minutes_with_age = models.IntegerField(null=True, blank=True)
    age_minutes = models.FloatField(null=True, blank=True)

    super_season = models.ForeignKey(SuperSeason, null=False)


    class Meta:
        #ordering = ("order", "name", "competition")
        ordering = ("order", "super_season__order2", "competition")
        #ordering = ("super_season", )


    def salaries(self):
        # This is terrible.
        from money.models import Salary
        return Salary.objects.filter(season=self.name)

        

    def goals(self):
        final_standings = self.standing_set.filter(final=True)
        if final_standings.count():
            data = final_standings.values_list('goals_for')
            return sum([(e[0] or 0) for e in data])
        else:
            #from goals.models import Goal
            #return Goal.objects.filter(game__season=self).count()
            from games.models import Game
            return Game.objects.filter(season=self).aggregate(Sum('goals'))['goals__sum']

    def goals_per_game(self):
        goals = self.goals()
        games = self.max_games()

        if goals is None or games in (0, None):
            return 0
        else:
            return goals / float(games)

    def games_with_attendance(self):
        return self.game_set.exclude(attendance=None).count()

    def games_with_attendance_percentage(self):
        return self.games_with_attendance() / float(self.max_games())

    def stadium_attendance(self):
        from places.models import Stadium

        games = self.game_set.exclude(attendance=None).exclude(home_team=None).exclude(stadium__capacity=None)
        
        attendance = defaultdict(int)
        game_dict = defaultdict(int)

        stadiums = set()

        for t,a,sn,sid in games.values_list('home_team__name', 'attendance', 'stadium__name', 'stadium'):
            key = (t,sn)
            attendance[key] += a
            game_dict[key] += 1
            stadiums.add(sid)

        capacities = dict(Stadium.objects.filter(id__in=stadiums).values_list('name', 'capacity'))

        make_item = lambda key: { 'team': key[0], 'stadium': key[1], 'capacity': capacities[key[1]], 'attendance': float(attendance[key]) / game_dict[key] }

        return [make_item(key) for key in attendance.keys()]


    def total_attendances(self):
        # This is a duplicate.

        d = defaultdict(int)
        games = self.game_set.exclude(attendance=None).exclude(home_team=None).values_list('home_team__name', 'attendance')

        for team, attendance in games:
            d[team] += attendance
            
        return d.items()
        


    def previous_game(self, game):
        # This doesn't really work. 

        from games.models import Game

        if game.date is None:
            return None

        same_day_games = Game.objects.filter(season=self, date=game.date, id__lt=game.id).order_by('-id')
        if same_day_games.exists():
            return same_day_games[0]

        else:
            games = Game.objects.filter(season=self, date__lt=game.date).order_by('-date', '-id')
            if games.exists():
                return games[0]
            else:
                return None
    
    def next_game(self, game):
        from games.models import Game

        if game.date is None:
            return None

        same_day_games = Game.objects.filter(season=self, date=game.date, id__gt=game.id).order_by('id')
        if same_day_games.exists():
            return same_day_games[0]
        else:
            games = Game.objects.filter(season=self, date__gt=game.date).order_by('date', 'id')
            if games.exists():
                return games[0]
            else:
                return None


    def stats_nationality_info(self):
        # Turn this into a templatetag.

        gpd = defaultdict(int)
        md = defaultdict(int)
        gd = defaultdict(int)

        for e in self.stat_set.values_list('player__birthplace__country__confederation', 'games_played', 'minutes', 'goals'):
            country, gp, minutes, goals = e
            if country is None:
                country = "unknown"

            if gp:
                gpd[country] += gp
            if minutes:
                md[country] += minutes
            if goals:
                gd[country] += goals

        make_item = lambda k: [k, gpd[k], md[k], gd[k]]

        return [make_item(e) for e in gpd.keys()]


    def average_date(self):
        if self.game_set.exclude(date=None).exists():
            dates = self.game_set.exclude(date=None).values_list('date')
            datetimes = [datetime.datetime(e.year, e.month, e.day) for [e] in dates]
            ordinal_datetimes = [e.toordinal() for e in datetimes]
            average_ordinal = sum(ordinal_datetimes) / float(len(ordinal_datetimes))
            return datetime.datetime.fromordinal(int(average_ordinal))
        return None


        

    def nationality_stats(self):
        stats = self.stat_set
        # Stat.objects.filter(season=self, competition=self.competition).
        return nationality_stats(stats)

    def confederation_stats(self):
        stats = self.stat_set
        # Stat.objects.filter(season=self, competition=self.competition).
        return confederation_stats(stats)



    def dates(self):
        try:
            year = int(self.name)
            start = datetime.datetime(year, 1, 1)
            end = datetime.datetime(year + 1, 12, 31)
        except ValueError:
            pass

        try:
            start_year, end_year = [int(e) for e in self.name.split('-')]
            pass
        except:
            pass


    def age_minutes_proportion(self):
        if self.minutes:
            return float(self.minutes_with_age) / self.minutes

    def average_age(self):
        if self.age_minutes:
            return self.age_minutes / self.minutes_with_age
            

    def __unicode__(self):
        return u"%s %s" % (self.name, self.competition.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Season, self).save(*args, **kwargs)


    def goal_distribution(self, ceiling=5):
        d = defaultdict(int)
        for game in self.game_set.exclude(home_team=None).exclude(team1_score=None):
            if game.home_score() == None:
                import pdb; pdb.set_trace()
            d[(min(game.home_score(), ceiling), min(game.away_score(), ceiling))] += 1
        return d


    def goal_distribution2(self, ceiling=5):
        gd = self.goal_distribution()
        d = {}
        for k in gd:
            home, away = k
            if home >= away:
                d[k] = gd[k]
            else:
                d[(away, home)] = gd[k]

        return d
            

    
    def previous_season(self):
        seasons = Season.objects.filter(competition=self.competition)
        index = list(seasons).index(self)
        if index > 0:
            return seasons[index - 1]
        else:
            return None

    def next_season(self):
        seasons = Season.objects.filter(competition=self.competition)
        index = list(seasons).index(self)
        next = index + 1
        if next < seasons.count():
            return seasons[next]
        else:
            return None


    def players(self):
        from stats.models import SeasonStat

        season_stats = SeasonStat.objects.filter(competition=self.competition, season=self)
        return set([e[0] for e in season_stats.values_list("player_id")])


    def players_diff(self, season):
        ids = self.players() - season.players()
        return Bio.objects.filter(id__in=ids)

    def players_added(self):
        if self.previous_season():
            return self.players_diff(self.previous_season())
        return []

    def players_lost(self):
        return 
        
       
    def get_next_name(self):
        try:
            name = int(self.name)
            return str(name + 1)
        except:
            # Need to do a regular expression?
            return None

            
    def first_standing(self):
        return self.standing_set.all()[0]


    def champion(self):
        from awards.models import AwardItem

        try:
            return AwardItem.objects.get(season=self, award__type='champion')
        except:
            return None

    def mvp(self):
        from awards.models import AwardItem

        # Need to expand for other names.
        try:
            return AwardItem.objects.get(season=self, award__type='mvp')
        except:
            return None



    def golden_boot(self):
        from awards.models import AwardItem
        try:
            return AwardItem.objects.get(season=self, award__name='Golden Boot').recipient
        except:
            goalscorers = self.stat_set.exclude(goals=None).exclude(goals=0).order_by('-goals', '-assists')
            if goalscorers.exists():
                return goalscorers[0].player
            else:
                return None





    def data_string(self):
        s = ''
        if self.standing_set.exists():
            s += 'Sg'
        if self.stat_set.exists():
            s += 'St'
        if self.game_set.exists():
            s += 'Gm'
        if self.goal_set.exists():
            s += 'Gl'
        return s
            
