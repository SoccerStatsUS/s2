from collections import defaultdict
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.db import transaction

from s2.teams.models import Team
from s2.competitions.models import Competition
from s2.stats.models import Stat


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


@transaction.commit_on_success
def generate_stats_generic(qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """
    stat_dict = {}
    for stat in qs.values():
        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']
        key = make_key(stat) 

        if key not in stat_dict:
            # This should set all necessary fields.
            stat_dict[key] = stat
        else:
            d = stat_dict[key]
            for key, value in stat.items():
                if key not in ('player_id', 'team_id', 'competition_id', 'season_id'):
                    if not d[key]:
                        d[key] = value
                    else:
                        if value:
                            d[key] += value


    for key, stat in stat_dict.items():
        stat.pop('id')
        stat.update(update_dict)
        Stat.objects.create(**stat)


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
        

def generate_team_stats():
    print "generating team stats"
    for team in Team.objects.all():
        stats = Stat.objects.filter(team=team)
        make_key = lambda s: (s['player_id'], s['team_id'])
        update = {'competition_id': None, 'season_id': None }
        generate_stats_generic(stats, make_key, update)


def generate_competition_stats():
    print "generating competition stats"
    for competition in Competition.objects.all():
        stats = Stat.objects.filter(competition=competition)
        make_key = lambda s: (s['player_id'], s['competition_id'])
        update = {'team_id': None, 'season_id': None }
        generate_stats_generic(stats, make_key, update)
            
                        
if __name__ == "__main__":
    generate()
