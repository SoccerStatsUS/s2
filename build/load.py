import datetime
import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 's2.build_settings'

from django.db import transaction
from django.db.utils import IntegrityError

from s2.awards.models import Award, AwardItem
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
    load_awards()
    load_drafts()
    load_stats()
    load_positions()
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
        try:
            Position.objects.create(**position)
        except:
            import pdb; pdb.set_trace()


@transaction.commit_on_success
def load_awards():
    print "loading awards"
    awards = set()
    award_dict = {}

    for item in soccer_db.awards.find():
        t = (item['competition'], item['award'])
        awards.add(t)

    for t in awards:
        competition, name = t

        # Finding because currently using NCAA awards but don't have ncaa standings.
        competition = Competition.objects.find(competition)
        # competition = Competition.objects.get(name=competition)
        a = Award.objects.create(competition=competition, name=name)
        award_dict[t] = a

    for item in soccer_db.awards.find():
        item['award'] = award_dict[(item['competition'], item['award'])]
        competition = item['award'].competition
        # NCAA seasons don't exist.
        item['season'] = Season.objects.find(competition=competition, name=item['season'])
        #item['season'] = Season.objects.get(competition=competition, name=item['season'])


        model_name = item.pop('model')
        if model_name == 'Bio':
            model = Bio
        elif model_name == 'Team':
            model = Team
        else:
            import pdb; pdb.set_trace()
            raise

        try:
            item['recipient'] = model.objects.find(item['recipient'], create=True)
        except:
            import pdb; pdb.set_trace()
            print item['recipient']
            continue

        item.pop('competition')        
        item.pop('_id')

        AwardItem.objects.create(**item)
        



@transaction.commit_on_success
def load_drafts():
    print "loading drafts"


    # Create a set of all possible drafts.
    drafts = set()
    for pick in soccer_db.drafts.find():
        try:
            t = (pick.get('competition'), pick['draft'])
        except:
            import pdb; pdb.set_trace()
        drafts.add(t)


    # Map competition, draft name to Draft objects.
    # Would be nice not to create these here.
    draft_dict = {}
    for t in drafts:
        competition, name = t
        competition = Competition.objects.find(name=competition)

        real = "USMNT" not in name

        d = Draft.objects.create(competition=competition, name=name, real=real)
        draft_dict[t] = d

    # Create picks
    for pick in soccer_db.drafts.find():

        pick['draft'] = draft_dict[(pick.get('competition'), pick['draft'])]
        pick['team'] = Team.objects.find(pick['team'], create=True)
        pick.pop('_id')

        if 'competition' in pick:
            pick.pop('competition')

        # Set the player reference.
        text = pick['text']
        if text.lower() == 'pass':
            player = None
        elif "SuperDraft" in text: # huh?
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

        if 'source' in game:
            game.pop('source')

        # Seem to have multiple Miami Fusion entries?
        try:
            Game.objects.create(**game)
        except IntegrityError:
            print game
        except ValueError:
            print game
            


@transaction.commit_on_success
def load_goals():
    # Looks like competition is unnecessary here.

    print "loading goals\n"
    # Use a sql insert here also.
    # Use dicts for team, game, bio.
    teams = Team.objects.team_dict()
    games = Game.objects.game_dict()
    bios = Bio.objects.bio_dict()


    l = []

    def create_goal(goal):
        team = goal['team']
        if team in teams:
            team_id = teams[team]
        else:
            team_id = Team.objects.find(team, create=True).id
            teams[team] = team_id

        player = goal['goal']
        if player in bios:
            bio_id = bios[player]
        else:
            bio_id = Bio.objects.find(player).id
            bios[player] = bio_id

        # Coerce to date to match dict.
        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)
        game_key = (team_id, d)

        if game_key in games:
            game_id = games[game_key]
        else:
            game_id = None
            print "No game match for %s" % goal

        if game_id:
            return {
                'date': goal['date'],
                'minute': goal['minute'],
                'team': Team.objects.get(id=team_id),
                'player': Bio.objects.get(id=bio_id),
                'game': Game.objects.get(id=game_id),
                }

    for goal in soccer_db.goals.find():
        g = create_goal(goal)
        if g:
            Goal.objects.create(**g)


# Experimental stuff.
def make_team_getter():
    teams = Team.objects.team_dict()

    def get_team(team):
        if team in teams:
            team_id = teams[team]
        else:
            team_id = Team.objects.find(team, create=True).id
            teams[team] = team_id

        return team_id

    return get_team

def make_bio_getter():
    bios = Bio.objects.bio_dict()

    def get_bio(name):
        if name in bios:
            bio_id = bios[name]
        else:
            bio_id = Bio.objects.find(name).id
            bios[name] = bio_id

        return bio_id

    return get_bio

        
def make_competition_getter():
    competitions = Competition.objects.as_dict()

    def get_competition(name):
        if name in competitions:
            cid = competitions[name]
        else:
            cid = Competition.objects.find(name).id
            competitions[name] = cid

        return cid

    return get_competition

    
@transaction.commit_on_success
def load_stats():
    # This takes way too fucking long.
    print "\nCreating stats\n"
    l = []

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    competition_getter = make_competition_getter()
    
    for i, stat in enumerate(soccer_db.stats.find(timeout=False)): # no timeout because this query takes forever.
        if i % 1000 == 0:
            print i

        if stat['name'] == '':
            continue

        team_id = team_getter(stat['team'])
        bio_id = bio_getter(stat['name'])
        competition_id = competition_getter(stat['competition'])
        #team = Team.objects.find(stat['team'],create=True)
        #bio = Bio.objects.find(name=stat['name'])
        #competition = Competition.objects.find(stat['competition'])
        # Turn these into dict calls with id's.
        competition = Competition.objects.get(id=competition_id)
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
            'player_id': bio_id,
            'team_id': team_id,
            'competition_id': competition_id,
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

    insert_sql("stats_stat", l)



@transaction.commit_on_success
def load_lineups():
    # Need to do this with raw sql and standard dict management functions.
    print "\nloading lineups\n"
    from django.db import connection



    teams = {}
    games = {}
    players = {}
    
    def create_appearance(a):

        # Setting find functions to memoize should do the same job.
        # Don't create all those extra references if not necessary.
        if not a['name']:
            print a
            return None

        if a['team'] in teams:
            team = teams[a['team']]
        else:
            team = Team.objects.find(a['team'], create=True)
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

    # Create the appearance objects.
    l = []
    for i, a in enumerate(soccer_db.lineups.find()):
        u = create_appearance(a)
        if u:
            l.append(u)

        if i % 5000 == 0:
            print i

    print "Creating appearances" # acutal objects.
    for e in l:
        Appearance.objects.create(**e)

    #insert_sql("lineups_appearance", l)
        
        

        
