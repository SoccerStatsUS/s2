from collections import defaultdict
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.db import transaction

from s2.teams.models import Team
from s2.stats.models import Stat


def generate():
    """
    Generate stats.
    """
    generate_career_stats()
    #generate_team_stats()


@transaction.commit_on_success
def generate_career_stats():
    print "Generating stats"


    print "Generating career stats."
    stat_dict = {}
    for stat in Stat.objects.all().values():
        key = stat['player_id']
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
        s = Stat.objects.create(**stat)
        print s
        print s.id
        


@transaction.commit_on_success
def generate_team_stats():
    stat_dict = {}
    print "Generating team stats."
    teams = Team.objects.all()
    for team in teams:
        print "Generating for %s" % team
        stats = Stat.objects.filter(team=team)
        for stat in stats.values():
            key = (stat['player_id'], stat['team_id'])
            # This should set team and player appropriately.
            if key not in stat_dict:
                stat_dict[key] = stat
            else:
                d = stat_dict[key]
                for key, value in stat.items():
                    if key in ('player', 'team', 'competition', 'season'):
                        pass
                    else:
                        if d[key]:
                            if value:
                                d[key] += value
                        else:
                            d[key] = value



    for key, stat in stat_dict.items():
        print key
        stat.update({
                'competition_id': None,
                'season_id': None,
                })
        stat.pop('id')
        Stat.objects.create(**stat)
            


                        
if __name__ == "__main__":
    generate()
