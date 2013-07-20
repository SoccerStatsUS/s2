import pymongo
import datetime

from bios.models import Bio
from competitions.models import Competition, Season
from games.models import Game
from goals.models import Goal
from teams.models import Team
from places.models import Country, State, City, Stadium
from sources.models import Source

connection = pymongo.Connection()
soccer_db = connection.soccer


class Getter(object):
    """
    An abstract getter object.
    """

    
    def __init__(self, model):
        self.model = model
        self.items = model.objects.to_dict()


    def get(e):
        if e not in self.items:
            self.items[e] = self.model.objects.find(e, create=True).id

        return self.items[e]


#def f():
#    tg = Getter(Team)
#    cg = Getter(Country)
#    sg = Getter(Source)



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


def make_country_getter():

    d = Country.objects.country_dict()

    def get_country(c):
        if c in d:
            return d[c]

        return None

    return get_country
    

def make_source_getter():
    """
    Retrieve sources efficiently
    """

    sources = Source.objects.source_dict()

    def get_source(source):

        if source.startswith('http'):
            for base, source_id in sources.items():
                if source.startswith(base):
                    return source_id

            # fallback
            s = Source.objects.create(name=source)
            sources[source] = s.id
            return s.id

        elif source in sources:
            return sources[source]

        else:
            s = Source.objects.create(name=source)
            sources[source] = s.id
            return s.id

    return get_source
    

# This is way too complex.
# I'm taking a break.
def make_city_getter():
    """
    
    """

    cg = make_city_pre_getter()
    
    def get_city(s):
        c = cg(s)

        state = country = None
        if c['state']:
            state = State.objects.get(name=c['state'])

        if c['country']:
            country = Country.objects.get(name=c['country'])
        
        return City.objects.get(name=c['name'], state=state, country=country)

    return get_city


def make_city_pre_getter():
    """
    Dissasseble a location string into city, state, and country pieces.
    City, state, and country are all optional, although country should (always?) 
    exist.
    e.g. Dallas, Texas -> {'name': 'Dallas', 'state': 'Texas', 'country': 'United States' }
    Cape Verde -> {'name': '', 'city': '', 'country': 'United States',
    """
    # Would like to add neighborhood to this.
    # Should this be part of normalize instead of here? Possibly.

    def make_state_abbreviation_dict():
        # Map abbreviation to state name, state country.
        d = {}
        for e in soccer_db.states.find():
            d[e['abbreviation']] = (e['name'], e.get('country'))

        return d


    def make_state_name_dict():
        d = {}
        for e in soccer_db.states.find():
            d[e['name']] = (e['name'], e.get('country'))

        return d

        

    country_name_set = set([e['name'].strip() for e in soccer_db.countries.find()])
    state_abbreviation_dict = make_state_abbreviation_dict()
    state_name_dict = make_state_name_dict()


    def get_dict(s):

        state = country = None

        if ',' in s:
            pieces = s.split(',')
            end = pieces[-1].strip()

            if end in state_abbreviation_dict:
                state, country = state_abbreviation_dict[end]

            elif end in state_name_dict:
                state, country = state_name_dict[end]

            elif end in country_name_set:
                country = end

        if country or state:
            name = ','.join(pieces[:-1])
        else:
            name = s

        # Change name to city.
        return {
            'name': name,
            'state': state,
            'country': country,
            }


    return get_dict


def make_bio_getter():
    """
    Retrieve bios easily.
    """

    bios = Bio.objects.bio_dict()

    def get_bio(name):
        name = name.strip()

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
        name = name.strip()

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
            if competition_id:
                competition = Competition.objects.get(id=competition_id)
            else:
                competition = None

            sid = Season.objects.find(name, competition).id
            seasons[key] = sid

        return sid


    return get_season


def make_game_getter():
    """
    Retrieve competitions easily.
    """

    game_team_map = Game.objects.id_dict()

    def getter(team_id, dt):

        # This is becoming a larger and larger problem.
        # Going to have to reconsider how we label games because of dateless games.

        if dt is None:
            print "Failed to find game for team %s on %s" % (team_id, dt)
            #import pdb; pdb.set_trace()
            gid = None
        else:
            # Not doing full game times yet...
            dx = datetime.date(dt.year, dt.month, dt.day) # Avoid datetime.date/datetime.datetime mismatch.
            key = (team_id, dx)
            if key in game_team_map:
                gid = game_team_map[key]
            else:
                print "Failed to find game for team %s on %s" % (team_id, dx)
                #import pdb; pdb.set_trace()
                gid = None
        
        return gid

    return getter




def make_game_result_getter():
    """
    Retrieve competitions easily.
    """

    result_map = Game.objects.result_dict()

    def getter(team_id, dt):

        # This is becoming a larger and larger problem.
        # Going to have to reconsider how we label games because of dateless games.

        if dt is None:
            print "Failed to find result for team %s on %s" % (team_id, dt)
            gid = None
        else:
            # Not doing full game times yet...
            dx = datetime.date(dt.year, dt.month, dt.day) # Avoid datetime.date/datetime.datetime mismatch.
            key = (team_id, dx)
            if key in result_map:
                gid = result_map[key]
            else:
                print "Failed to find game result for team %s on %s" % (team_id, dx)
                #import pdb; pdb.set_trace()
                gid = None
        
        return gid

    return getter




def make_goal_getter():
    """
    Retrieve competitions easily.
    """

    goal_map = Goal.objects.unique_dict()

    def getter(team_id, player_id, minute, dt):
        own_goal_player_id = None
        dx = datetime.date(dt.year, dt.month, dt.day) # Avoid datetime.date/datetime.datetime mismatch.
        key = (team_id, player_id, own_goal_player_id, minute, dx)
        if key in goal_map:
            gid = goal_map[key]
        else:
            print "Failed to find goal for team %s on %s" % (team_id, dx)
            gid = None
        
        return gid

    return getter
