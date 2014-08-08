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
        home_standing = Standing.objects.get(date=g.date, team=g.team1).triple()
        away_standing = Standing.objects.get(date=g.date, team=g.team2).triple()
    else:
        home_goals, away_goals = g.team2_score, g.team1_score        
        home_standing = Standing.objects.get(date=g.date, team=g.team2).triple()
        away_standing = Standing.objects.get(date=g.date, team=g.team1).triple()

    shootout_winner = g.shootout_winner

    for gs in g.gamestat_set.all():
        team = gs.team.name
        player = gs.player.name
        assists = gs.assists or 0
        
        #gx = Goal.objects.filter(player=gs.player, date=g.date)
        #goal_minutes = [e.minute for e in gx]
        #goal_final = goal_minutes + (5-len(goal_minutes)) * ['']

        dt = g.date.strftime("%m/%d/%Y")

        lx = [
            dt,
            g.stadium.name,
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
            gs.on,
            gs.off,
            gs.minutes,
            ] # + goal_final # + assist_final

        #s = "\t".join(lx)
        
        l.append(lx)
    return l
                


def process_games():
    games = Game.objects.filter(competition__slug='major-league-soccer').exclude(not_played=True).exclude(season__name='2014').order_by('id')
    l = []
    for game in games:
        print game.id
        try:
            l.extend(export_game(game))
        except:
            import pdb; pdb.set_trace()

    return l


def create_csv(l):
    l2 = ["\t".join([unicode(a) for a in e]) for e in l]
    return "\n".join(l2)



def process_goals():
    goals = Goal.objects.filter(game__competition__slug='major-league-soccer').exclude(game__season__name='2014').select_related().order_by('date')
    l = []

    for i, goal in enumerate(goals):
        print(i)

        if goal.player:
            scorer = goal.player.name
        elif goal.own_goal_player:
            scorer = goal.own_goal_player.name
        else:
            scorer = None

        assists = [e.player.name for e in goal.assist_set.all()]

        assists_final = assists + (2-len(assists)) * ['']
        
        
        dt = goal.date.strftime("%m/%d/%Y")

        x = [
            dt,
            goal.team.name,
            goal.minute,
            goal.own_goal,
            scorer,
            assists_final[0],
            assists_final[1],
            ]

                                   

        """
        d = {
            'date': goal.date,
            'minute': goal.minute
            'team': goal.team,
            'scorer': goal.player.name,
            'assists': assists,
            }"""

        l.append(x)

    return l
        

            
def process():
    games = process_games()
    goals = process_goals()
    
    s = [unicode(e) for e in games]
    s2 = [unicode(e) for e in goals]

    f = open('games.txt', 'w')
    f.write(s.encode('utf8'))
    f.close()

    f2 = open('goals.txt', 'w')
    f2.write(s2.encode('utf8'))
    f2.close()

    
        
                                    
        
        
        
        


    
