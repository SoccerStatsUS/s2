from collections import defaultdict
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import transaction

from bios.models import Bio
from competitions.models import Competition
from games.models import Game, GameMinute
from goals.models import Goal
from lineups.models import Appearance
from positions.models import Position
from standings.models import Standing
from stats.models import Stat
from teams.models import Team

from utils import insert_sql, timer

def generate():
    """
    Generate stats.
    """

    # Needs to be first. 
    generate_position_standings()

    generate_career_stats()
    generate_competition_stats()
    generate_team_stats()
    generate_competition_standings()
    generate_team_standings()

    generate_game_data_quality()
    #generate_game_minutes()


@timer
@transaction.commit_on_success
def generate_game_minutes():
    """
    Generate all game minutes that we can.
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
        

        
    
@timer
@transaction.commit_on_success
def generate_game_data_quality():
    """
    Generate game data quality info.
    """
    print "Generating game data quality."

    lineup_games = set([e[0] for e in Appearance.objects.values_list("game")])
    goal_games = set([e[0] for e in Goal.objects.values_list("game")])
    
    for e in Game.objects.all():
        if e.id in lineup_games:
            e.completeness = 2
        elif e.id in goal_games:
            e.completeness = 1
        elif e.goals == 0:
            e.completeness = 1
        else:
            e.completeness = 0
        e.save()

@transaction.commit_on_success
def generate_stats_generic(qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """
    final_dict = {}
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id')
    for stat in qs.values():
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
        stat.update(update_dict)
        Stat.objects.create(**stat)


def generate_career_stats():
    """
    Generate 
    """
    print "generating career stats"
    make_key = lambda s: s['player_id']
    update = {
        'team_id': None,
        'competition_id': None,
        'season_id': None,
        }
    generate_stats_generic(Stat.objects.all(), make_key, update)    
    #generate_career_plus_minus()
        
@timer
def generate_team_stats():
    print "generating team stats"
    for team in Team.objects.all():
        stats = Stat.objects.filter(team=team)
        make_key = lambda s: (s['player_id'], s['team_id'])
        update = {'competition_id': None, 'season_id': None }
        generate_stats_generic(stats, make_key, update)


@timer
def generate_competition_stats():
    print "generating competition stats"
    for competition in Competition.objects.all():
        stats = Stat.objects.filter(competition=competition)
        make_key = lambda s: (s['player_id'], s['competition_id'])
        update = {'team_id': None, 'season_id': None }
        generate_stats_generic(stats, make_key, update)



@transaction.commit_on_success
def generate_standings_generic(qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """
    # Seems like memory leaks are making this not work for nearly enough stats.

    final_dict = {}
    excluded = ('team_id', 'competition_id', 'season_id')
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
    print "Calculating standings."
    Position.objects.generate_standings()


@timer
def generate_player_standings():
    """
    Generate all player standings for all players across all stats.
    """
    # This does not work because it's leaking memory like crazy.

    for i, b in enumerate(Bio.objects.all()):
        b.calculate_standings()
        if i % 1000 == 0:
            print i



    
        

def generate_plus_minus(appearance_qs):

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
        
    
            
                        
if __name__ == "__main__":
    generate_team_standings()


