from competitions.models import Competition,Season
#from games.models import Game
from lineups.models import Appearance
from stats.models import Stat


def check_stats(competition_slug, season_name=None):
    season = None
    c = Competition.objects.get(slug=competition_slug)
    if season_name:
        season = Season.objects.get(competition=c,name=season_name)
    
    d = {}
    

    if season:
        appearances = Appearance.objects.filter(game__season=season)
    else:
        appearances = Appearance.objects.filter(game__competition=c)
    


    i = 0
    
    print appearances.count()
    for a in appearances:
        if i % 1000 == 0:
            print i
        i += 1

        key = (a.player, a.team, a.game.season)
        if key not in d:
            d[key] = {
                'games_played': 0,
                'games_started':0,
                }
            
        s = d[key]

        s['games_played'] += 1
        if a.on == 0:
            s['games_started'] += 1

            #import pdb; pdb.set_trace()

    if season:
        stats = Stat.objects.filter(season=season)
    else:
        stats = Stat.objects.filter(competition=c)

    stats = stats.order_by('season', 'team')


    problems = []


    # Add check that all generated stats exist really.
    for stat in stats:
        key = (stat.player, stat.team, stat.season)
        if key not in d:
            problems.append((stat, None))
            print "Missing: %s" % str(key)

        else:
            sd = d[key]
            if stat.games_played != sd['games_played'] or stat.games_started != sd['games_started']:
                problems.append((stat, sd))
                print "Mismatch %s" %  str(key)
    
    print len(problems)
        
    import pdb; pdb.set_trace()

    x = 5
    
