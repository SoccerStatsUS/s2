from django.db import transaction
import pymongo

connection = pymongo.Connection()
soccer_db = connection.soccer


@transaction.commit_on_success
def load_bios():
    # Need to delete tables first.

    from s2.bios.models import Bio
    for bio in soccer_db.bios.find():
        Bio.objects.create(bio)


@transaction.commit_on_success
def load_games():
    from s2.games.models import Game
    for game in soccer_db.games.find():
        Game.objects.create(game)
        
