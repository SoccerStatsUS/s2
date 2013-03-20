import datetime

from competitions.models import Competition
from games.models import Game
from teams.models import Team





def calculate_iffhs(team, competition_mapping, start=None, end=None):
    games = Game.objects.team_filter(team).exclude(date=None)

    if start:
        games = games.filter(date__gte=start)

    if end:
        games = games.filter(date__lte=end)


    points = 0

    competitions = competition_mapping.keys()

    for game in games:
        if game.competition in competitions:
            cpoints = competition_mapping[game.competition]

            result = game.result(team)

            if result == 't':
                points += cpoints / 2.0

            elif result == 'w':
                points += cpoints
                
    return points





def best_2000():
    cx = lambda s: Competition.objects.get(slug=s)
    d = {
        cx('major-league-soccer'): 3,
        cx('concacaf-champions-league'): 9,
        cx('concacaf-champions-cup'): 9,
        cx('us-open-cup'): 3,
        }

    team_ids = set(Competition.objects.get(slug='major-league-soccer').standing_set.all().values_list('team'))
    team_ids = [e[0] for e in team_ids]


    teams = Team.objects.filter(id__in=team_ids)

    td = {}
    for team in teams:
        points = calculate_iffhs(team, d, start=datetime.date(2000, 1, 1), end=datetime.date(2011, 1, 1))
        td[team] = points

    return td

    


