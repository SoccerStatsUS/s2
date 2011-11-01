import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 's2.settings'

from django.db import transaction
from django.db.utils import IntegrityError

from s2.bios.models import Bio
from s2.competitions.models import Competition, Season
from s2.drafts.models import Draft, Pick
from s2.games.models import Game
from s2.goals.models import Goal
from s2.lineups.models import Appearance
from s2.positions.models import Position
from s2.teams.models import Team
from s2.stats.models import Stat
from s2.standings.models import Standing

from s2.utils import insert_sql


connection = pymongo.Connection()
soccer_db = connection.soccer



def load():
    load_teams()
    load_standings()
    load_bios()
    load_drafts()
    load_stats()
    load_positions()

    return



    load_games()
    load_goals()

    load_lineups()


# These all just apply some very basic formatting 
# and apply foreign keys.

@transaction.commit_on_success
def load_positions():
    print "loading positions"
    for position in soccer_db.positions.find():
        position.pop('_id')
        position['team'] = Team.objects.find(position['team'], create=True)
        position['person'] = Bio.objects.find(position['person'])
        Position.objects.create(**position)

@transaction.commit_on_success
def load_drafts():
    print "loading drafts"
    drafts = set()
    draft_dict = {}
    for pick in soccer_db.drafts.find():
        t = (pick['competition'], pick['draft'])
        drafts.add(t)

    for t in drafts:
        competition, name = t
        competition = Competition.objects.get(name=competition)
        d = Draft.objects.create(competition=competition, name=name)
        draft_dict[t] = d
        

    for pick in soccer_db.drafts.find():
        pick['draft'] = draft_dict[(pick['competition'], pick['draft'])]
        pick['team'] = Team.objects.find(pick['team'], create=True)
        pick.pop('competition')
        pick.pop('_id')
        
        text = pick['text']
        if text.lower() == 'pass':
            player = None
        elif "SuperDraft" in text:
            player = None
        else:
            player = Bio.objects.find(text)
        pick['player'] = player
        Pick.objects.create(**pick)
        



        

@transaction.commit_on_success
def load_teams():
    print "loading teams"
    for team in soccer_db.teams.find():
        team.pop('_id')
        Team.objects.create(**team)


@transaction.commit_on_success
def load_standings():
    print "loading standings\n"
    for standing in soccer_db.standings.find():
        standing.pop('_id')
        try:
            team_string = standing.pop('name')
        except:
            import pdb; pdb.set_trace()
        standing['team'] = Team.objects.find(team_string, create=True)
        standing['competition'] = Competition.objects.find(standing['competition'])
        standing['season'] = Season.objects.find(standing['season'], standing['competition'])
        Standing.objects.create(**standing)


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
        game['competition'] = Competition.objects.find(game['competition'])
        game['season'] = Season.objects.find(game['season'], game['competition'])
        game['home_team'] = Team.objects.find(game['home_team'], create=True)
        game['away_team'] = Team.objects.find(game['away_team'], create=True)
        game.pop('_id')
        if 'url' in game:
            game.pop('url')

        if 'year' in game:
            game.pop('year')

        # Seem to have multiple Miami Fusion entries?
        try:
            Game.objects.create(**game)
        except IntegrityError:
            print game


@transaction.commit_on_success
def load_goals():
    print "loading goals\n"
    # Use a sql insert here also.
    # Use dicts for team, game, bio.
    teams = Team.objects.team_dict()
    games = Game.objects.game_dict()
    bios = Bio.objects.bio_dict()


    l = []

    def create_goal(goal):
        team = goal['team']
        if goal['team'] in teams:
            team_id = teams[team]
        else:
            team_id = Team.objects.find(team).id
            teams[team] = team_id

        player = goal['player']
        if player in bios:
            bio_id = bios[player]
        else:
            bio_id = Bio.objects.find(player).id
            bios[player] = bio_id

        game_key = (team_id, goal['date'])
        if game_key in games:
            game_id = games[game_key]
        else:
            game_id = None


        if game_id:
                l.append({
                        'date': goal['date'],
                        'minute': goal['minute'],
                        'team_id': team_id,
                        'player_id': bio_id,
                        'game_id': game_id,
                        })

    insert_sql("games_game", l)
    
@transaction.commit_on_success
def load_stats():
    # need to create stats with sql as well.
    print "\nCreating stats\n"
    l = []
    for i, stat in enumerate(soccer_db.stats.find()):
        if i % 1000 == 0:
            print i

        if stat['name'] == '':
            continue

        # Turn these into dict calls with id's.
        team = Team.objects.find(stat['team'],create=True)
        bio = Bio.objects.find(name=stat['name'])
        competition = Competition.objects.find(stat['competition'])
        season = Season.objects.find(stat['season'], competition)


        # Should be in soccerdata.merge.
        for k in 'games_started', 'games_played', 'minutes', 'shots', 'shots_on_goal', \
                'fouls_committed', 'fouls_suffered', 'yellow_cards', 'red_cards':
            if stat.get(k) == '':
                stat[k] = None

        for k in 'goals', 'assists':
            if stat.get(k) == '':
                stat[k] = 0


        
        l.append({
            'player_id': bio.id,
            'team_id': team.id,
            'competition_id': competition.id,
            'season_id': season.id,
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

    print "Creating appearances"
    insert_sql("stats_stat", l)



@transaction.commit_on_success
def load_lineups():
    # Need to do this with raw sql.
    print "\nloading lineups\n"
    from django.db import connection

    
    teams = {}
    games = {}
    players = {}
    
    def create_appearance(a):

        # Setting find functions to memoize should to the same job.
        # Don't create all those extra references if not necessary.
        if not a['player']:
            print a
            return None

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
                 
        if a['player'] in players:
            player = players[a['player']]
        else:
            player = Bio.objects.find(a['player'])
            players[a['player']] = player

            

        if game:
            return {
                'team_id': team.id,
                'game_id': game.id,
                'player_id': player.id,
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
    insert_sql("lineups_appearance", l)
        
        

        
