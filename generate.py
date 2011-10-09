from collections import defaultdict
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.db import transaction

from s2.stats.models import Stat



@transaction.commit_on_success
def generate_stats():
    print "Generating stats"


    print "Generating career stats."
    stat_dict = {}
    for stat in Stat.objects.all().values():
        key = stat['player_id']
        print key
        if key not in stat_dict:
            stat_dict[key] = stat
        else:
            d = stat_dict[key]
            for key, value in stat.items():
                if key in ('player_id', 'team_id', 'competition_id', 'season_id'):
                    pass
                else:
                    if d[key]:
                        if value:
                            d[key] += value
                    else:
                        d[key] = value

    for stat in stat_dict.values():
        stat.update({
                'team_id': None,
                'competition_id': None,
                'season_id': None,
                })
        stat.pop('id')
        print stat
        Stat.objects.create(**stat)
        

    """
    print "Generating competition stats."
    competitions = Competition.objects.all()
    for competition in competitions:

        stat_dict = {}
        stats = Stat.objects.filter(competition=competition)
        for stat in stats:
            key = stat['player']
            if key not in stat_dict:
                stat_dict[key] = stat
            else:
                d = stat_dict[key]
                d['player'] = key
                for key, value in stat.items():
                    if key in ('player', 'team', 'competition', 'season'):
                        pass
                    else:
                        d[key] += value

        for stat in stat_dict.items():
            stat.update({
                    'team': None,
                    'competition': competition,
                    'season': None,
                    })
            Stat.objects.create(**stat)
            
"""

                        
if __name__ == "__main__":
    generate_stats()
