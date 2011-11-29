from collections import defaultdict
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.db import transaction

from s2.bios.models import Bio
from s2.competitions.models import Competition
from s2.lineups.models import Appearance
from s2.standings.models import Standing
from s2.stats.models import Stat
from s2.teams.models import Team
from s2.utils import timer


def generate():
    """
    Generate stats.
    """
    # Might want to generate these before inserting them
    # So we don't have duplicates.
    # Save them in a tmp file?
    generate_career_stats()
    generate_competition_stats()
    generate_team_stats()
    generate_competition_standings()
    generate_team_standings()


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


@transaction.commit_on_success
def generate_standings_generic(qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """
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


def generate_career_stats():
    print "generating career stats"
    make_key = lambda s: s['player_id']
    # Turn this into a list.
    update = {
        'team_id': None,
        'competition_id': None,
        'season_id': None,
        }
    generate_stats_generic(Stat.objects.all(), make_key, update)    
    #generate_career_plus_minus()


def generate_player_standings():
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

    
    
            
                        
if __name__ == "__main__":
    generate_team_standings()
