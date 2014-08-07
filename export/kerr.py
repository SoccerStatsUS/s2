# Code to export data for Craig Kerr.

from games.models import Game
from goals.models import Goal
from standings.models import Standing


def export_game(g):
    l = []
    

    
    home_team = g.home_team
    away_team = g.away_team()
    if g.team1 == home_team:
        home_goals, away_goals = g.team1_score, g.team2_score
        home_standing = Standing.objects.get(date=g.date, team=g.team1)
        away_standing = Standing.objects.get(date=g.date, team=g.team2)
    else:
        home_goals, away_goals = g.team2_score, g.team1_score        
        home_standing = Standing.objects.get(date=g.date, team=g.team2)
        away_standing = Standing.objects.get(date=g.date, team=g.team1)

    shootout_winner = g.shootout_winner

    for gs in g.gamestat_set.all():
        team = gs.team.name
        player = gs.player.name
        assists = gs.assists or 0
        
        gx = Goal.objects.filter(player=gs.player, date=g.date)
        goal_minutes = [e.minute for e in gx]
        goal_final = goal_minutes + (5-len(goal_minutes)) * ['']

        lx = [
            g.date,
            g.stadium,
            g.attendance,
            home_team,
            home_goals,
            home_standing,
            away_team,
            away_goals,
            away_standing,
            shootout_winner,
            team,
            player,
            gs.goals,
            assists,
            ] + goal_final # + assist_final

        #s = "\t".join(lx)
        
        l.append(lx)
    return l
                


def process():
    games = Game.objects.filter(competition__slug='major-league-soccer').exclude(not_played=True).order_by('id')
    l = []
    for game in games:
        print game.id
        try:
            l.extend(export_game(game))
        except:
            import pdb; pdb.set_trace()

    return l


def create_csv(l):
    l2 = ["\t".join(e) for e in l]
    return "\n".join(l2)
    
        
                                    
        
        
        
        


    
