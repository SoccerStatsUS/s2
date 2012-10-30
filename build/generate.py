from collections import defaultdict, Counter
import datetime
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'

from django.db import transaction
from django.db.models import Count

from bios.models import Bio
from competitions.models import Competition, Season
from drafts.models import Draft, Pick
from games.models import Game, GameMinute
from goals.models import Goal
from lineups.models import Appearance
from positions.models import Position
from sources.models import Source
from standings.models import Standing
from stats.models import Stat, CareerStat
from teams.models import Team
from utils import insert_sql, timer


@timer
def generate():
    """
    Generate stats.
    """

    # Need to choose one.
    # Generate coaching stats!
    #generate_position_standings()
    #generate_position_stats()

    generate_game_data_quality()

    set_draft_picks()

    generate_source_data()

    generate_career_stats()
    generate_competition_stats()
    generate_team_stats()
    generate_competition_standings()
    generate_team_standings()
    generate_season_data()

    generate_player_standings()

    #generate_game_minutes()



@timer
@transaction.commit_on_success
def generate_player_standings():
    results = Game.objects.values_list('id', 'team1', 'team1_result', 'team2', 'team2_result')
    result_map = {}
    for gid, t1, t1r, t2, t2r in results:
        result_map[(gid, t1)] = t1r
        result_map[(gid, t2)] = t2r

    players = set()
    standings = defaultdict(int)
    appearances = Appearance.objects.values_list('game', 'team', 'player')
    for game, team, player in appearances:
        result = result_map[(game, team)]
        standings[(player, result)] += 1
        players.add(player)

    for pid in players:
        w, l, t = standings[(pid, 'w')], standings[(pid, 'l')], standings[(pid, 't')]
        if w or l or t:
            try:
                c = CareerStat.objects.get(player=pid)
            except:
                continue
            c.wins, c.losses, c.ties = w, l, t
            c.save()
        
        
        


def set_draft_picks():

    # Not bothering parsing since this has only happened one time.
    d = Draft.objects.get(competition__slug='major-league-soccer', name='SuperDraft', season__name='2002')
    picks = Pick.objects.filter(text__contains='SuperDraft')
    for pick in picks:
        number = int(pick.text.lower().split('pick')[0].strip().replace('#', ''))
        target = Pick.objects.get(draft=d, number=number)
        pick.pick = target
        pick.save()

@timer
def generate_source_data():
    print "Generating source data."
    sources = Source.objects.annotate(game_count=Count('game'), stat_count=Count('stat'))
    for source in sources:
        source.games = source.game_count
        source.stats = source.stat_count
        source.save()
    
        


@timer
@transaction.commit_on_success
def generate_season_data():
    # Generate season data including average age, nationality data (somehow)
    print "Generating season data."

    minutes_dict = defaultdict(int)
    minutes_with_age_dict = defaultdict(int)
    age_minutes_dict = defaultdict(int)

    for season, minutes, age in Appearance.objects.values_list('game__season', 'minutes', 'age'):
        if minutes:
            minutes_dict[season] += minutes
            if age:
                minutes_with_age_dict[season] += minutes
                am = minutes * age
                age_minutes_dict[season] += am
        
    for sid, minutes in minutes_dict.items():
        minutes_with_age = minutes_with_age_dict[sid]
        age_minutes = age_minutes_dict[sid]

        print 'Setting season %s' % sid        
        s = Season.objects.get(id=sid)
        s.minutes = minutes
        s.minutes_with_age = minutes_with_age
        s.age_minutes = age_minutes
        s.save()

    
    """

        from lineups.models import Appearance
        appearances = Appearance.objects.filter(game__season=self)
        if not appearances.exists():
            return {}
        else:
            minutes_with_age = 0
            age_minutes = 0
            age_bucket_minutes = defaultdict(int)
            nationality_minutes = defaultdict(int)
            
            for appearance in appearances:
                if appearance.age:
                    minutes_with_age += appearance.minutes
                    age_minutes += appearance.age * appearance.minutes
                    age_bucket_minutes[int(appearance.age)] += appearance.minutes

                bp = appearance.player.birthplace
                if bp and bp.country:
                    nationality_minutes[bp.country] += appearance.minutes

            return {
                'minutes_with_age': minutes_with_age,
                'age_minutes': age_minutes,
                'age_bucket_minutes': age_bucket_minutes,
                'nationality_minutes': nationality_minutes,
                }

             """


def calculate_standings(team, games=None):
    # Do this with a dict, not a game object.

    if games is None:
        games = Game.objects.team_filter(position.team)

    wins = losses = ties = 0
    for game in games:
        r = game.result(team)

        if r == 'w':
            wins += 1
        elif r == 'l':
            losses += 1
        elif r == 't':
            ties += 1

    return wins, losses, ties

            
    
@timer
@transaction.commit_on_success
def generate_game_data_quality():
    """
    Generate game data quality info.
    """
    print "Quality data for all games."


    global_starters = Appearance.objects.filter(on=0).exclude(off=0)

    starter_map = Counter([e[0] for e in global_starters.values_list('game')])
    goal_map = Counter([e[0] for e in Goal.objects.values_list('game')])

    for game in Game.objects.all():
        game.starter_count = starter_map.get(game.id, 0)
        game.goal_count = goal_map.get(game.id, 0)
        game.save()
    

@transaction.commit_on_success
def generate_stats_generic(table, qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """

    #print "Merging stats."
    final_dict = {}

    # Don't try to add these items.
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id', 'source_id')


    for stat in qs.values():

        # Set unaddable values to none.
        for k,v  in stat.items():
            if v in ('?', 'None', '-'):
                stat[k] = None



        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']
        key = make_key(stat) 
        # Create a new entry for this stat type
        if key not in final_dict:
            # This should set all necessary fields.
            final_dict[key] = stat
        else:
            # 
            d = final_dict[key]
            for key, value in stat.items():
                if key not in excluded: 
                    if not d[key]:
                        d[key] = value
                    else:
                        if value:
                            try:
                                d[key] += value
                            except:
                                import pdb; pdb.set_trace()
                                x = 5


    for key, stat in final_dict.items():
        stat.pop('id')
        for e in update_dict.keys():
            if e in stat:
                stat.pop(e)
        
        # update_dict seems unnecessary at this point. Those values aren't in the given stat.
        #stat.update(update_dict)

    insert_sql(table, final_dict.values())
    #insert_sql("stats_stat", final_dict.values())
        #Stat.objects.create(**stat)


@timer
def generate_career_stats():
    """
    Generate career stats for all players,
    generate from individual stat objects.
    """
    # Need to exclude indoor stats from career stats.
    print "generating career stats"
    make_key = lambda s: s['player_id']
    update = {
        'team_id': None,
        'competition_id': None,
        'season_id': None,
        }
    generate_stats_generic("stats_careerstat", Stat.objects.filter(competition__code='soccer'), make_key, update)    
    #generate_career_plus_minus()
        
@timer
def generate_team_stats():
    print "generating team stats"
    for team in Team.objects.all():
        stats = Stat.objects.filter(team=team)
        make_key = lambda s: (s['player_id'], s['team_id'])
        update = {'competition_id': None, 'season_id': None }
        generate_stats_generic('stats_teamstat', stats, make_key, update)


@timer
def generate_competition_stats():
    print "generating competition stats"
    for competition in Competition.objects.all():
        stats = Stat.objects.filter(competition=competition)
        make_key = lambda s: (s['player_id'], s['competition_id'])
        update = {'team_id': None, 'season_id': None }
        generate_stats_generic('stats_competitionstat', stats, make_key, update)



@transaction.commit_on_success
def generate_standings_generic(qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """
    # Seems like memory leaks are making this not work for nearly enough stats.

    final_dict = {}
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id', 'division', 'group')
    for standing in qs.values():
        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']

        for k,v  in standing.items():
            if v == 'None':
                standing[k] = None

        key = make_key(standing) 
        if key not in final_dict:
            # This should set all necessary fields.
            final_dict[key] = standing
        else:
            d = final_dict[key]
            for key, value in standing.items():
                if key not in excluded:
                    if not d[key]:
                        d[key] = value
                    else:
                        # Check for None values.
                        if value:
                            try:
                                d[key] += value
                            except:
                                import pdb; pdb.set_trace()
                                x = 5

    for key, standing in final_dict.items():
        standing.pop('id')
        standing.update(update_dict)
        s = Standing.objects.create(**standing)



@timer
def generate_competition_standings():
    print "generating competition standings"
    """
    Generate all-time standings for each competition.
    """
    for competition in Competition.objects.all():
        standings = Standing.objects.filter(competition=competition).exclude(season=None)
        make_key = lambda s: (s['team_id'], s['competition_id'])
        update = {'season_id': None }
        generate_standings_generic(standings, make_key, update)

@timer
def generate_team_standings():
    print "generating team standings"
    for team in Team.objects.all():
        standings = Standing.objects.filter(team=team).exclude(season=None)
        make_key = lambda s: s['team_id']
        update = {'season_id': None, 'competition_id': None }
        generate_standings_generic(standings, make_key, update)


@timer
def generate_position_standings():
    """Generate standings for all positions."""
    print "Calculating standings for positions."
    Position.objects.generate_standings()





@timer
@transaction.commit_on_success
def generate_position_stats():
    # Generate stats for non-players. Coaches, Owners, etc.
    # Need to start by initializing a list of all games.

    for position in Position.objects.order_by('person'):
        if position.end is None:
            end = datetime.date.today()
        else:
            end = position.end

        if position.start:
            games = Game.objects.team_filter(position.team).filter(date__gte=position.start, date__lte=end)
            if games.exists():
                try:
                    print "Creating result stats for %s games for %s - %s at %s" % (games.count(), position.person, position.name, position.team)
                except:
                    print "Creating result stats."
                position.wins, position.losses, position.ties = calculate_standings(position.team, games)
                position.save()
        



def generate_plus_minus(appearance_qs):
    """
    Generate the +/- for a given queryset.
    """

    print "Generating plus_minus"
    d = defaultdict(int)

    for (i, a) in enumerate(appearance_qs.values()):
        if i % 1000 == 0:
            print i
            
        try:
            key = a['player']
        except:
            import pdb; pdb.set_trace()
        try:
            d[key] += a.goal_differential
        except:
            "Cannot get +/- for %s" % a
    return d


@transaction.commit_on_success
def generate_career_plus_minus():
    print "generating career plus minus"
    plus_minus = generate_plus_minus(Appearance.objects.all())
    career_stat_dict = Stat.career_stats.to_dict()

    for i, (k, v) in enumerate(plus_minus.items()):
        if i % 100 == 0:
            print i
        s = career_stat_dict[k]
        s.plus_minus = v
        s.save()


@timer
@transaction.commit_on_success
def generate_game_minutes():
    """
    Generate all game minutes that we can.
    These are single minute slices of a game.
    Really intensive cpu use.
    """
    print "Generating game minutes"

    l = []
    print "Creating score for %s games" % Game.objects.count()
    for i, e in enumerate(Game.objects.all()):
        if i % 1000 == 0:
            print "Making scores for %s" % i
        
        l.extend(e.game_scores_by_minute())

    # Just want to know how long this takes.
    @timer
    def insert_game_minutes():
        print "Generating %s game minutes" % len(l)
        insert_sql("games_gameminute", l)

    insert_game_minutes()



def generate_top_attendances(qs=None):
    """
    Generate a rolling list of top attendances.
    """
    # Put this in GameManager?

    if qs is None:
        qs = Game.objects.all()

    qs = qs.order_by('date')
    
    max = -1

    gids = []

    for gid, attendance in qs.values_list("id", "attendance"):
        if gid in (7591, 8202, 8184, 11119, 8671, 3809):
            continue

        if attendance:
            if attendance > max:
                max = attendance
                gids.append(gid)

    return Game.objects.filter(id__in=gids).order_by('date')
    
            
                        
if __name__ == "__main__":
    generate()
    """
    t = generate_top_attendances()
    for g in t:
        print g
        print g.id
        print g.attendance
        print
    #generate_team_standings()
    """




