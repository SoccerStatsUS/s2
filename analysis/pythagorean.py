
from collections import defaultdict

from teams.models import Team



def pythagorean_expectation(games):

    team_ids = set()
    team_id_list = games.values_list('team1', 'team2')

    for e in team_id_list:
        team_ids.add(e[0])
        team_ids.add(e[1])

    teams = Team.objects.filter(id__in=team_ids)

    gf = defaultdict(int)
    ga = defaultdict(int)

    for game in games:
        
        if game.team1_score and game.team2_score:
            gf[game.team1] += game.team1_score
            ga[game.team2] += game.team1_score

            ga[game.team1] += game.team2_score
            gf[game.team2] += game.team2_score

    pythagorean = []
    for team in teams:
        tgf = gf[team]
        tga = ga[team]

        # Need to tune this...
        exponent = 2

        expectation = 1.0 / (1 + ( tga / float(tgf))**exponent)
        pythagorean.append((team, expectation))

    return pythagorean

                        
        
        
