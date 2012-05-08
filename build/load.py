import datetime
import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'

from django.db import transaction
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from awards.models import Award, AwardItem
from bios.models import Bio
from competitions.models import Competition, Season
from drafts.models import Draft, Pick
from games.models import Game
from goals.models import Goal
from lineups.models import Appearance
from places.models import City, Stadium
from positions.models import Position
from teams.models import Team
from stats.models import Stat
from standings.models import Standing

from utils import insert_sql, timer

connection = pymongo.Connection()
soccer_db = connection.soccer


# These probably need to be in load_utils or something.
# This isn't the place.
def make_team_getter():
    """
    Retrieve teams easily.
    """

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
    """
    Retrieve bios easily.
    """

    bios = Bio.objects.bio_dict()

    def get_bio(name):
        if name in bios:
            bio_id = bios[name]
        else:
            bio_id = Bio.objects.find(name).id
            bios[name] = bio_id

        return bio_id

    return get_bio


def make_stadium_getter():
    """
    Retrieve bios easily.
    """

    stadiums = Stadium.objects.as_dict()

    def getter(name):
        if name in stadiums:
            sid = stadiums[name]
        else:
            sid = Stadium.objects.find(name).id
            stadiums[name] = sid
        return sid

    return getter

        
def make_competition_getter():
    """
    Retrieve competitions easily.
    """
    competitions = Competition.objects.as_dict()


    def get_competition(name):
        if name in competitions:
            cid = competitions[name]
        else:
            cid = Competition.objects.find(name).id
            competitions[name] = cid

        return cid

    return get_competition


def make_season_getter():
    """
    Retrieve competitions easily.
    """

    seasons = Season.objects.as_dict()

    def get_season(name, competition_id):
        key = (name, competition_id)
        if key in seasons:
            sid = seasons[key]
        else:
            competition = Competition.objects.get(id=competition_id)
            sid = Season.objects.find(name, competition).id
            seasons[key] = sid

        return sid


    return get_season




def make_game_getter():
    """
    Retrieve competitions easily.
    """

    game_team_map = Game.objects.game_dict()

    def getter(team_id, dt):
        # Not doing full game times yet...
        dx = datetime.date(dt.year, dt.month, dt.day) # Avoid datetime.date/datetime.datetime mismatch.
        key = (team_id, dx)
        if key in game_team_map:
            gid = game_team_map[key]
        else:
            print "Failed to find for %s, %s" % (team_id, dx)
            gid = None
        
        return gid

    return getter


def load():
    load_teams()
    load_stadiums()

    # Game data
    load_standings()
    load_games()

    # Person data
    load_bios()
    #load_awards()
    load_drafts()
    load_positions()

    # Mixed data
    load_stats()
    load_goals()
    load_lineups()



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


    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    for item in soccer_db.awards.find():
        t = (item['competition'], item['award'])
        awards.add(t)

    for t in awards:
        competition, name = t

        # Should be able to use a competition_getter here?
        # Using find because currently using NCAA awards but don't have ncaa standings.



        if competition:
            competitoin = Competition.objects.find(competition)

        a = Award.objects.create(competition=competition, name=name)
        award_dict[t] = a


    for item in soccer_db.awards.find():
        item.pop('_id')

        # So we can have a season, a year, both, or neither for an award item
        item['award'] = award_dict[(item['competition'], item['award'])]
        item.pop('competition')        

        # NCAA seasons don't exist.
        # Would be good to use get otherwise to ensure we have good data.
        if competition:
            competition_id = item['award'].competition.id
            item['season'] = season_getter(item['season'], competition_id)
            item['season'] = Season.objects.get(id=item['season'])

        model_name = item.pop('model')
        if model_name == 'Bio':
            model = Bio
        elif model_name == 'Team':
            model = Team
        else:
            import pdb; pdb.set_trace()
            raise

        item['recipient'] = model.objects.find(item['recipient'], create=True)
        AwardItem.objects.create(**item)


@transaction.commit_on_success
def load_drafts():
    print "loading drafts"

    competition_getter = make_competition_getter()
    team_getter = make_team_getter()

    # Create the set of drafts.
    drafts = set()
    for pick in soccer_db.drafts.find():
        t = (pick.get('competition'), pick['draft'])
        drafts.add(t)


    # Map competition, draft name to Draft objects.
    # Would be nice not to create these here.=
    draft_dict = {}
    for t in drafts:

        competition, name = t

        real = True

        competition_id = competition_getter(competition)
        competition = Competition.objects.get(id=competition_id)
        d = Draft.objects.create(competition=competition, name=name, real=real)

        draft_dict[t] = d

    # Create picks
    picks = []
    for pick in soccer_db.drafts.find():
        pick.pop('_id')

        # draft, text, player, position, team
        draft = draft_dict[(pick.get('competition'), pick['draft'])]

        team_id = team_getter(pick['team'])

        if 'competition' in pick:
            pick.pop('competition')

        # Set the player reference.
        text = pick['text']
        if text.lower() == 'pass':
            player_id = None

        # Draft picks were "drafted" in the MLS Allocation Draft.
        elif "SuperDraft" in text:
            player_id = None
        else:
            player_id = Bio.objects.find(text).id

        picks.append({
                'draft_id': draft.id,
                'player_id': player_id,
                'team_id': team_id,
                'text': text,
                'position': pick['position'],
                })

    for e in picks:
        try:
            Pick.objects.create(**e)
        except:
            import pdb; pdb.set_trace()
    #insert_sql("drafts_pick", picks)
        
        

@transaction.commit_on_success
def load_teams():
    print "loading teams"
    for team in soccer_db.teams.find():
        team.pop('_id')
        Team.objects.create(**team)

@transaction.commit_on_success
def load_stadiums():
    print "loading stadiums"
    for stadium in soccer_db.stadiums.find():
        stadium.pop('_id')
        stadium['slug'] = slugify(stadium['name'])

        
        if 'renovations' in stadium:
            stadium.pop('renovations')
        if 'source' in stadium:
            stadium.pop('source')
        
        if stadium['architect']:
            stadium['architect'] = Bio.objects.find(stadium['architect'])

        try:
            Stadium.objects.create(**stadium)
        except:
            import pdb; pdb.set_trace()
        x = 5



@transaction.commit_on_success
def load_standings():
    print "loading standings\n"
    for standing in soccer_db.standings.find():
        standing.pop('_id')
        standing['team'] = Team.objects.find(standing['team'], create=True)
        standing['competition'] = Competition.objects.find(standing['competition'])
        standing['season'] = Season.objects.find(standing['season'], standing['competition'])
        Standing.objects.create(**standing)


@transaction.commit_on_success
def load_bios():
    for bio in soccer_db.bios.find():
        print "Creating bio for %s" % bio['name']
        bio.pop('_id')

        if not bio['name']:
            import pdb; pdb.set_trace()
            print "NO BIO: %s" % str(bio)
            continue

        # nationality should be many-to-many
        if 'nationality' in bio:
            bio.pop('nationality')



        bd = {}

        # Set birthplace to a city. 
        # Skipping this for the time being.
        if False and 'birthplace' in bio:
            d = get_location(bio['birthplace'])
            if d:
                bd['birthplace'] = City.objects.find(d)
            else:
                bd['birthplace'] = None

        for key in 'name', 'height', 'birthdate', 'height', 'weight':
            if key in bio:
                bd[key] = bio[key] or None

        Bio.objects.create(**bd)


@transaction.commit_on_success
def load_games():
    print "loading %s games\n" % soccer_db.games.count()

    stadium_getter = make_stadium_getter()
    team_getter = make_team_getter()
    competition_getter = make_competition_getter()    


    for game in soccer_db.games.find():
        game.pop('_id')

        if game.get('stadium'):
            game['stadium'] = stadium_getter(game['stadium'])
            game['stadium'] = Stadium.objects.get(id=game['stadium'])
        
        game['competition'] = competition_getter(game['competition'])
        game['competition'] = Competition.objects.get(id=game['competition'])
        game['season'] = Season.objects.find(game['season'], game['competition'])



        game['team1'] = team_getter(game['team1'])
        game['team1'] = Team.objects.get(id=game['team1'])
        game['team2'] = team_getter(game['team2'])
        game['team2'] = Team.objects.get(id=game['team2'])        
        game['goals'] = game['team1_score'] + game['team2_score']
        
        if game['referee']:
            game['referee'] = Bio.objects.find(game['referee'])
        else:
            game['referee'] = None

        for e in 'url', 'home_team', 'year', 'source', 'sources':
            if e in game:
                game.pop(e)

        # There are lots of problems with the NASL games, 
        # And probably ASL as well. Need to spend a couple
        # of hours repairing those schedules.
        try:
            Game.objects.create(**game)
        except:
            print "Skipping game %s" % game
            #import pdb; pdb.set_trace()

        x = 5


@transaction.commit_on_success
def load_goals():
    print "loading goals\n"

    # Use a sql insert here also.
    # Use dicts for team, game, bio.
    teams = Team.objects.team_dict()
    games = Game.objects.game_dict()
    bios = Bio.objects.bio_dict()
    stadium_getter = make_stadium_getter()


    l = []

    def create_goal(goal):
        if goal.get('stadium'):
            goal['stadium'] = stadium_getter(goal['stadium'])


        
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


    
@transaction.commit_on_success
def load_stats():
    # Stats takes forever.

    print "\nCreating stats\n"

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    l = []    
    for i, stat in enumerate(soccer_db.stats.find(timeout=False)): # no timeout because this query takes forever.
        if i % 1000 == 0:
            print i

        if stat['name'] == '':
            #import pdb; pdb.set_trace()
            continue


        team_id = team_getter(stat['team'])
        bio_id = bio_getter(stat['name'])
        competition_id = competition_getter(stat['competition'])
        season_id = season_getter(stat['season'], competition_id)

        l.append({
            'player_id': bio_id,
            'team_id': team_id,
            'competition_id': competition_id,
            'season_id': season_id,
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


@timer
@transaction.commit_on_success
def load_lineups():
    # Need to do this with raw sql and standard dict management functions.
    print "\nloading lineups\n"
    from django.db import connection


    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    game_getter = make_game_getter()

    games = {}
    
    def create_appearance(a):

        # Setting find functions to memoize should do the same job.
        # Don't create all those extra references if not necessary.
        if not a['name']:
            print a
            return None

        team_id = team_getter(a['team'])
        player_id = bio_getter(a['name'])
        game_id = game_getter(team_id, a['date'])

        if not game_id:
            print "Cannot create %s" % a
            return {}


        """
        if game.date and player.birthdate:
            age = (game.date - player.birthdate).days / 365.25
        else:
            age = None
        """

        return {
            'team_id': team_id,
            'game_id': game_id,
            'player_id': player_id,
            'on': a['on'],
            'off': a['off'],
            'team_original_name': '',
            #'age': age,
            }

    # Create the appearance objects.
    l = []
    for i, a in enumerate(soccer_db.lineups.find()):
        u = create_appearance(a)
        if u:
            l.append(u)

        if i % 5000 == 0:
            print i

    print "Creating appearances"

    for e in l:
        try:
            insert_sql("lineups_appearance", [e])
        except:
            import pdb; pdb.set_trace()
