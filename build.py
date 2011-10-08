import itertools
import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.core.management import call_command
from django.db import transaction
from django.db.utils import IntegrityError

from s2 import settings
from s2.bios.models import Bio
from s2.games.models import Game
from s2.goals.models import Goal
from s2.lineups.models import Appearance
from s2.teams.models import Team
from s2.stats.models import Stat

connection = pymongo.Connection()
soccer_db = connection.soccer



def build():
    delete()
    load()

@transaction.commit_on_success
def delete():
    for model in (Bio, Game, Team, Goal):
        model.objects.all().delete()


def load():
    load_teams()
    load_bios()
    load_games()
    load_goals()
    load_stats()
    load_lineups()


# These all just apply some very basic formatting 
# and apply foreign keys.


@transaction.commit_on_success
def load_teams():
    print "loading teams"
    for team in soccer_db.teams.find():
        team.pop('_id')
        Team.objects.create(**team)


@transaction.commit_on_success
def load_bios():
    for bio in soccer_db.bios.find():

        if not bio['name']:
            print "NO BIO: %s" % str(bio)
            continue

        bio.pop('_id')
        if 'nationality' in bio:
            bio.pop('nationality')
        print "Creating bio for %s" % bio['name']


        bd = {}
        for key in 'name', 'height', 'birthdate', 'birthplace', 'height', 'weight':
            if key in bio:
                bd[key] = bio[key] or None

        Bio.objects.create(**bd)


@transaction.commit_on_success
def load_games():
    print "loading games\n"

    for game in soccer_db.games.find():
        game['home_team'] = Team.objects.find(game['home_team'], create=True)
        game['away_team'] = Team.objects.find(game['away_team'], create=True)
        game.pop('_id')
        # Delete this once year is removed.
        game.pop('year')


        # Seem to have multiple Miami Fusion entries?
        try:
            Game.objects.create(**game)
        except IntegrityError:
            print game


@transaction.commit_on_success
def load_goals():
    print "loading goals\n"

    def create_goal(goal):
        team = Team.objects.find(goal['team'])
        game = Game.objects.find(team=team, date=goal['date'])
        bio = Bio.objects.find(name=goal['name'])

        if game:
            try:
                Goal.objects.create(**{
                        'date': goal['date'],
                        'minute': goal['minute'],
                        'team': team,
                        'player': bio,
                        'game': game,
                        })
            except:
                import pdb; pdb.set_trace()
                x = 5
        

    # Load this after loading team, game, and bio.
    for i, goal in enumerate(soccer_db.goals.find()):
        create_goal(goal)
        if i % 2000 == 0:
            print i


@transaction.commit_on_success
def load_lineups():
    print "\nloading lineups\n"
    from django.db import connection

    
    teams = {}
    games = {}
    players = {}
    
    def create_appearance(a):

        # Setting find functions to memoize should to the same job.
        # Don't create all those extra references if not necessary.
        if a['team'] in teams:
            team = teams[a['team']]
        else:
            team = Team.objects.find(a['team'])
            teams[a['team']] = team

        t = (team, a['date'])
        if t in games:
            game = games[t]
        else:
            game = Game.objects.find(team=team, date=a['date'])
            games[t] = game
                 
        if a['name'] in players:
            player = players[a['name']]
        else:
            player = Bio.objects.find(a['name'])
            players[a['name']] = player

            

        if game:
            return {
                'team': team,
                'game': game,
                'player': player,
                'on': a['on'],
                'off': a['off'],
                }


    l = []
    for i, a in enumerate(soccer_db.lineups.find()):
        u = create_appearance(a)
        if u:
            l.append(u)

        if i % 5000 == 0:
            print i

    print "Creating appearances"
    for e in l:
        Appearance.objects.create(**e)
        
        

@transaction.commit_on_success
def load_stats():
    print "\nCreating stats\n"
    for i, stat in enumerate(soccer_db.stats.find()):
        if i % 1000 == 0:
            print i

        if stat['name'] == '':
            continue

        team = Team.objects.find(stat['team'],create=True)
        bio = Bio.objects.find(name=stat['name'])

        # Should be in soccerdata.merge.
        for k in 'games_started', 'games_played', 'minutes', 'shots', 'shots_on_goal', \
                'fouls_committed', 'fouls_suffered', 'yellow_cards', 'red_cards':
            if stat.get(k) == '':
                stat[k] = None

        for k in 'goals', 'assists':
            if stat.get(k) == '':
                stat[k] = 0
        
        try:
            d = {
                'player': bio,
                'team': team,
                'competition': stat.get('competition'),
                'season': stat.get('season'),
                'games_started': stat.get('games_started'),
                'games_played': stat.get('games_played'),
                'minutes': stat.get('minutes'),
                'goals': stat.get('goals'),
                'assists': stat.get('assists'),
                'shots': stat.get('shots'),
                'shots_on_goal': stat.get('shots_on_goal'),
                'fouls_committed': stat.get('fouls_committed'),
                'fouls_suffered': stat.get('fouls_suffered'),
                'yellow_cards': stat.get('yellow_cards'),
                'red_cards': stat.get('red_cards'),
                }
            Stat.objects.create(**d)
        except:
            import pdb; pdb.set_trace()
            x = 5

# Testing and stuff.

def load_mongo_teams():
    s = set()
    for e in soccer_db.games.find():
        s.add(e['home_team'])
        s.add(e['away_team'])
    return sorted(list(s))


def get_unloaded_teams():
    for e in load_mongo_teams():
        try:
            Team.objects.find(e)
        except:
            print e
    


        


if __name__ == "__main__":
    load()
        
