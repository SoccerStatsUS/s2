from django.db.models import Sum, Avg
from django.db import models
from django.template.defaultfilters import slugify

from collections import defaultdict

from bios.models import Bio

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
            


class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            print "Creating competition %s" % name
            return Competition.objects.create(name=name)


    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d




class Competition(models.Model):
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
    
    #international = models.BooleanField()

    objects = CompetitionManager()

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    def make_abbreviation(self):
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
        return Award.objects.filter(competition=self, name='MVP').exists()


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.abbreviation:
            self.abbreviation = self.make_abbreviation()
            
        super(Competition, self).save(*args, **kwargs)



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





class SeasonManager(models.Manager):

    def find(self, name, competition):
        try:
            return Season.objects.get(name=name, competition=competition)
        except:
            if type(competition) in (int, str, unicode):
                competition = Competition.objects.get(id=competition)
            return Season.objects.create(name=name, competition=competition)

    def as_dict(self):
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




class Season(models.Model):
    """
    A season of a competition.
    """
    # Considering removing the competition dependency and making season refer to a given period of time.
    # A CompetitionSeason would then refer to a season/competition unit.

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    competition = models.ForeignKey(Competition, null=True)
    competition_original_name = models.CharField(max_length=255)

    objects = SeasonManager()

    minutes = models.IntegerField(null=True, blank=True)
    minutes_with_age = models.IntegerField(null=True, blank=True)
    age_minutes = models.FloatField(null=True, blank=True)


    class Meta:
        ordering = ("name", "competition")


    def total_attendance(self):
        games = self.game_set.exclude(attendance=None)
        return games.aggregate(Sum('attendance'))['attendance__sum']
        
    def average_attendance(self):
        games = self.game_set.exclude(attendance=None)
        return int(games.aggregate(Avg('attendance'))['attendance__avg'])

    def games_with_attendance(self):
        return self.game_set.exclude(attendance=None).count()



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
        return u"%s %s" % (self.name, self.competition)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Season, self).save(*args, **kwargs)


    def goals(self):
        final_standings = self.standing_set.filter(final=True)
        if final_standings.count():
            data = final_standings.values_list('goals_for')
            return sum([e[0] for e in data])
        else:
            #from goals.models import Goal
            #return Goal.objects.filter(game__season=self).count()
            from games.models import Game
            return Game.objects.filter(season=self).aggregate(Sum('goals'))['goals__sum']


    def goals_per_game(self): 
        if self.standing_set.exists():
            data = self.standing_set.values_list('goals_for', 'games')
            goals = sum([e[0] for e in data])
            games = sum([e[1] for e in data])
            if games == 0:
                return 0

        else:
            from games.models import Game
            goals = self.goals()
            games = Game.objects.filter(season=self).count()

        return float(goals) / games


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
            return unicode(name + 1)
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
            return AwardItem.objects.get(season=self, award__name='MVP')
        except:
            return None



    def golden_boot(self):
        from awards.models import AwardItem
        try:
            return AwardItem.objects.get(season=self, award__name='Golden Boot').recipient
        except:
            goalscorers = self.stat_set.exclude(goals=None).order_by('-goals', '-assists')
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
            
