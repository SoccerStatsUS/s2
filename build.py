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
    #load_teams()
    load_bios()
    load_games()
    load_goals()
    load_stats()


def load_fixtures():
    # Not working?
    call_command("loaddata", "' + 'teams.yaml' + '", verbosity=0)


def load_teams():
    print "loading teams"
    load_goal_teams()


def load_bios():
    print "loading bios"
    load_mongo_bios()
    #load_goal_bios()


def load_games():
    print "loading games"
    load_db_games()
    #load_goal_games()


def load_goals():
    print "loading goals"
    load_db_goals()


@transaction.commit_on_success
def load_mongo_bios():
    for bio in soccer_db.bios.find():
        bio.pop('_id')
        bio.pop('nationality')
        print "Creating bio for %s" % bio['name']
        Bio.objects.create(**bio)




@transaction.commit_on_success
def load_db_games():
    for game in soccer_db.games.find():
        game['home_team'] = Team.objects.find(game['home_team'])
        game['away_team'] = Team.objects.find(game['away_team'])
        game.pop('_id')
        # Delete this once year is removed.
        game.pop('year')


        # Seem to have multiple Miami Fusion entries?
        try:
            Game.objects.create(**game)
        except IntegrityError:
            print game


# These suck. Get rid of them.
@transaction.commit_on_success
def load_goal_teams():
    s = set()
    for goal in soccer_db.goals.find():
        s.add(goal['team'])
    for e in s:
        Team.objects.find(name=e)

@transaction.commit_on_success
def load_goal_bios():
    s = set()
    for goal in soccer_db.goals.find():
        s.add(goal['name'])
    for e in s:
        Bio.objects.find(e)

@transaction.commit_on_success
def load_goal_games():
    s = set()
    for goal in soccer_db.goals.find():
        team = Team.objects.find(goal['team'])
        s.add((team, goal['date']))
    for team, date in s:
        Game.objects.find(team=team, date=date)

        

@transaction.commit_on_success
def load_db_goals():

    # Load this after loading team, game, and bio.
    for goal in soccer_db.goals.find():
        team = Team.objects.find(goal['team'])
        game = Game.objects.find(team=team, date=goal['date'])
        bio = Bio.objects.find(name=goal['name'])

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

@transaction.commit_on_success
def load_stats():
    for stat in soccer_db.stats.find():
        team = Team.objects.find(stat['team'])
        bio = Bio.objects.find(name=stat['name'])
        
        Stat.objects.create(**{
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
                })


        


if __name__ == "__main__":
    load()
        
