import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.core.management import call_command
from django.db import transaction
from django.db.utils import IntegrityError

from s2 import settings
from s2.bios.models import Bio
from s2.games.models import Game
from s2.teams.models import Team

connection = pymongo.Connection()
soccer_db = connection.soccer


def build():
    delete()
    load()

@transaction.commit_on_success
def delete():
    for model in (Bio, Game, Team):
        model.objects.all().delete()


def load():
    #load_fixtures()
    load_bios()
    load_games()
    load_goals()

def load_fixtures():
    call_command("loaddata", "' + 'teams.yaml' + '", verbosity=0)


@transaction.commit_on_success
def load_bios():
    for bio in soccer_db.bios.find():
        bio.pop('_id')
        Bio.objects.create(**bio)


@transaction.commit_on_success
def load_games():
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

@transaction.commit_on_success
def load_goals():
    for goal in soccer_db.goals.find():
        team = Team.objects.find(goal['team'])
        game = Game.objects.find(team=team, date=goal['date'])
        goal['team'] = team
        goal['game'] = game

        goal.pop('_id')
        goal.pop('competition')
        goal.pop('season')



if __name__ == "__main__":
    load()
        
