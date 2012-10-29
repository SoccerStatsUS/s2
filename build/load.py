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
from money.models import Salary
from news.models import NewsSource
from places.models import Country, State, City, Stadium
from positions.models import Position
from sources.models import Source
from stats.models import Stat
from standings.models import Standing
from teams.models import Team

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

    # Watch out for contingencies here.
    # Places depend only on other places.
    # Bio depends on places.
    # Stadium depends on places and bios.
    # Teams depends on (nothing?)
    # Standings depends on Bio, Team, Competition, and Season
    # Games depends on Team, Stadium, City, Bio.
    # etc.

    # Georgraphical data.
    #load_geo()

    # Non-game data.
    load_sources()
    load_places()

    load_bios()
    load_salaries()

    load_stadiums()

    # Simple sport data
    load_competitions()
    load_teams()


    load_standings()

    # List data
    # Put this before standings?
    load_awards()
    load_drafts()
    load_positions()

    # Complex game data
    load_games()

    # Mixed data
    load_stats()
    load_goals()
    load_lineups()

    # Analysis data
    #load_news()



def load_geo():
    import os
    from django.contrib.gis.utils import LayerMapping
    from places.models import WorldBorder
    world_mapping = {
        'fips' : 'FIPS',
        'iso2' : 'ISO2',
        'iso3' : 'ISO3',
        'un' : 'UN',
        'name' : 'NAME',
        'area' : 'AREA',
        'pop2005' : 'POP2005',
        'region' : 'REGION',
        'subregion' : 'SUBREGION',
        'lon' : 'LON',
        'lat' : 'LAT',
        'mpoly' : 'MULTIPOLYGON',
        }

    world_shp = '/home/chris/www/soccerdata/data/places/world/TM_WORLD_BORDERS-0.3.shp'

    lm = LayerMapping(WorldBorder, world_shp, world_mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=True)


def run(verbose=True):
    lm = LayerMapping(WorldBorder, world_shp, world_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)    



def load_sources():
    for source in soccer_db.sources.find():
        source.pop('_id')
        source['games'] = source['stats'] = 0
        Source.objects.create(**source)


def load_places():

    for country in soccer_db.countries.find():
        country.pop('_id')
        country['slug'] = slugify(country['name'])
        country['confederation'] = country['confederation'] or ''
        country['subconfederation'] = country['subconfederation'] or ''
        Country.objects.create(**country)


    for state in soccer_db.states.find():
        state.pop('_id')
        state['country'] = Country.objects.get(name=state['country'])
        state['slug'] = slugify(state['name'])
        State.objects.create(**state)

    cg = make_city_pre_getter()

    city_set  = set()

    for city in soccer_db.cities.find():
        c = cg(city['name'])

        if c['state']:
            c['state'] = State.objects.get(name=c['state'])


        if c['country']:
            c['country'] = Country.objects.get(name=c['country'])

        # Create slugs
        if c['state']:
            slug = "%s %s" % (c['name'], c['state'].abbreviation)

        elif c['country']:
            slug = "%s %s" % (c['name'], c['country'])

        else:
            slug = c['name']

        c['slug'] = slugify(slug)

        city_set.add(tuple(sorted(c.items())))

    for e in city_set:
        City.objects.create(**dict(e))


@timer
@transaction.commit_on_success
def load_positions():
    print "\nloading positions\n"
    for position in soccer_db.positions.find():
        position.pop('_id')
        position['team'] = Team.objects.find(position['team'], create=True)
        position['person'] = Bio.objects.find(position['person'])
        #try:
        Position.objects.create(**position)
        #except:
        #    import pdb; pdb.set_trace()
        #    x = 5


@timer
@transaction.commit_on_success
def load_awards():
    print
    print "\nloading awards\n"
    awards = set()
    award_dict = {}


    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    # Create the set of all awards.
    for item in soccer_db.awards.find():
        t = (item['competition'], item['award'], item.get('type', ''))
        awards.add(t)

    # Create all awards.
    for t in awards:
        competition, name, award_type = t

        # Using find because currently using NCAA awards but don't have ncaa standings.
        # Should be able to switch to competition_getter here.
        if competition:
            competition = Competition.objects.find(competition)

        a = Award.objects.create(competition=competition, name=name, type=award_type)
        award_dict[t] = a


    # Create awardItems.
    for item in soccer_db.awards.find().sort('recipient', 1):
        item.pop('_id')

        # So we can have a season, a year, both, or neither for an award item
        item['award'] = award_dict[(item['competition'], item['award'], item.get('type', ''))]
        item.pop('competition')        

        if 'type' in item:
            item.pop('type')

        # NCAA seasons don't exist.
        # Would be good to use get otherwise to ensure we have good data.
        if item['award'].competition:
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

@timer
@transaction.commit_on_success
def load_drafts():
    print "\nloading drafts\n"

    competition_getter = make_competition_getter()
    team_getter = make_team_getter()

    # Create the set of drafts.

    for draft in soccer_db.drafts.find().sort('team', 1):
        draft.pop('_id')
        competition_id = competition_getter(draft['competition'])        
        competition = Competition.objects.get(id=competition_id)
        draft['competition'] = competition
        Draft.objects.create(**draft)

    # Create picks
    picks = []
    for pick in soccer_db.picks.find():
        pick.pop('_id')


        # draft, text, player, position, team
        draft = Draft.objects.get(name=pick.get('draft'), season=pick.get('season'), competition__name=pick.get('competition'))

        team_id = team_getter(pick['team'])

        if pick.get('former_team'):
            former_team_id = team_getter(pick['former_team'])
        else:
            former_team_id = None

        # Set the player reference.
        text = pick['text']

        # Draft picks were "drafted" in the MLS Allocation and Dispersal drafts.
        if "SuperDraft" in text:
            player_id = None
        elif text.lower() == 'pass':
            player_id = None
        else:
            player_id = Bio.objects.find(text).id

        picks.append({
                'draft_id': draft.id,
                'player_id': player_id,
                'team_id': team_id,
                'text': text,
                'position': pick.get('position') or '',
                'former_team_id': former_team_id,
                'number': pick['number'],
                })

    for e in picks:
        Pick.objects.create(**e)

    #insert_sql("drafts_pick", picks)
        
        
@transaction.commit_on_success
def load_news():
    print "loading news"
    for e in soccer_db.news.find():
        e.pop('_id')
        NewsSource.objects.create(**e)

@timer
@transaction.commit_on_success
def load_teams():
    print "loading teams"
    for team in soccer_db.teams.find():
        team.pop('_id')
        Team.objects.create(**team)

@transaction.commit_on_success
def load_competitions():
    print "loading competitions"
    for c in soccer_db.competitions.find():
        c.pop('_id')
        try:
            Competition.objects.create(**c)
        except:
            import pdb; pdb.set_trace()
            x =5 


@transaction.commit_on_success
def load_stadiums():
    print "loading stadiums"

    cg = make_city_getter()

    for stadium in soccer_db.stadiums.find():
        stadium.pop('_id')
        stadium['slug'] = slugify(stadium['name'])

        stadium['city'] = cg(stadium['location'])

        
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


@timer
@transaction.commit_on_success
def load_standings():
    print "loading standings\n"
    for standing in soccer_db.standings.find().sort('team', 1):
        standing.pop('_id')
        standing['team'] = Team.objects.find(standing['team'], create=True)
        standing['competition'] = Competition.objects.find(standing['competition'])
        standing['season'] = Season.objects.find(standing['season'], standing['competition'])
        Standing.objects.create(**standing)

@timer
@transaction.commit_on_success
def load_bios():
    cg = make_city_getter()


    # Find which names are used so we can only load these bios.
    fields = [('lineups', 'name'), ('goals', 'goal'), ('stats', 'name'), ('awards', 'recipient'), ('picks', 'text')]
    names = set()
    for coll, key in fields:
        names.update([e[key] for e in soccer_db[coll].find()])

    # Load bios.
    for bio in soccer_db.bios.find().sort('name', 1):

        if bio['name'] not in names:
            #print "Skipping %s" % bio['name']
            continue


        try:
            print "Creating bio for %s" % bio['name']
        except:
            print "Created bio."

        bio.pop('_id')

        if not bio['name']:
            import pdb; pdb.set_trace()
            print "NO BIO: %s" % str(bio)
            continue

        # nationality should be many-to-many
        if 'nationality' in bio:
            bio.pop('nationality')

        bd = {}

        for key in 'name', 'height', 'birthdate', 'height', 'weight':
            if key in bio:
                bd[key] = bio[key] or None

        if bio.get('birthplace'):
            bd['birthplace'] = cg(bio['birthplace'])

        if bio.get('deathplace'):
            bd['deathplace'] = cg(bio['deathplace'])

        bd['hall_of_fame'] = bio.get('hall_of_fame', False)

        Bio.objects.create(**bd)


@transaction.commit_on_success
def load_salaries():
    bg = make_bio_getter()

    for e in soccer_db.salaries.find():
        e.pop('_id')
        
        bio = bg(e['name'])
        b = Bio.objects.get(id=bio)
        Salary.objects.create(
            person=b,
            amount=e['base'],
            season=e['year'].strip()
            )
                 

@timer
@transaction.commit_on_success
def load_games():
    print "\nloading %s games\n" % soccer_db.games.count()

    stadium_getter = make_stadium_getter()
    team_getter = make_team_getter()
    competition_getter = make_competition_getter()    
    source_getter = make_source_getter()
    bio_getter = make_bio_getter()

    city_getter = make_city_getter()

    games = []

    for game in soccer_db.games.find().sort('date', 1):

        stadium_id = city_id = None
        if game.get('stadium'):
            stadium_id = stadium_getter(game['stadium'])
            city_id = Stadium.objects.get(id=stadium_id).id

        elif game.get('city'):
            city_id = city_getter(game['city']).id

        elif game.get('location'):
            city_id = city_getter(game['location']).id

        competition_id = competition_getter(game['competition'])
        #game['competition'] = Competition.objects.get(id=game['competition'])
        season_id = Season.objects.find(game['season'], competition_id).id

        team1_id = team_getter(game['team1'])
        team2_id = team_getter(game['team2'])

        home_team_id = None
        if game.get('home_team'):
            home_team_id = team_getter(game['home_team'])

        goals = (game['team1_score'] or 0) + (game['team2_score'] or 0)

        referee_id = linesman1_id = linesman2_id = linesman3_id = None
        if game['referee']:
            referee = bio_getter(game['referee'])

        if game.get('linesman1'):
            linesman1 = bio_getter(game['linesman1'])

        if game.get('linesman2'):
            linesman2 = bio_getter(game['linesman2'])

        if game.get('linesman3'):
            linesman3 = bio_getter(game['linesman3'])

        source = None
        source_url = ''
        if game.get('sources'):
            source = game['sources'][-1]
        elif game.get('source'):
            source = game['source']

        if source and source.startswith('http'):
            source_url = source

        source_id = None
        if source:
            source_id = source_getter(source)

        result_unknown = game.get('result_unknown') or False
        played = game.get('played') or True
        forfeit = game.get('forfeit') or False
        minigame = game.get('minigame') or False

        minutes = game.get('minutes') or 90

        neutral = game.get('neutral') or False
        attendance = game.get('attendance')

        # There are lots of problems with the NASL games, 
        # And probably ASL as well. Need to spend a couple
        # of hours repairing those schedules.

        games.append({
                'date': game['date'],
                'team1_id': team1_id,
                'team1_original_name': game['team1_original_name'],
                'team2_id': team2_id,
                'team2_original_name': game['team2_original_name'],

                'team1_score': game['team1_score'],
                'official_team1_score': game.get('official_team1_score'),
                'team2_score': game['team2_score'],
                'official_team2_score': game.get('official_team2_score'),

                'team1_result': game['team1_result'],
                'team2_result': game['team2_result'],

                'result_unknown': result_unknown,
                'played': played,
                'forfeit': forfeit,

                'goals': goals,
                'minigame': minigame,

                'minutes': minutes,
                'competition_id': competition_id,
                'season_id': season_id,

                'home_team_id': home_team_id,
                'neutral': neutral,

                'stadium_id': stadium_id,
                'city_id': city_id,
                'location': game.get('location', ''),
                'notes': '',
                'attendance': attendance,
                
                'referee_id': referee_id,
                'linesman1_id': linesman1_id,
                'linesman2_id': linesman2_id,
                'linesman3_id': linesman3_id,

                'source_id': source_id,
                'source_url': source_url,
                })

                


        """
        try:
            Game.objects.create(**game)
        except:
            print "Skipping game %s" % game
            import pdb; pdb.set_trace()
            x = 5
        """
    insert_sql("games_game", games)

@timer
@transaction.commit_on_success
def load_goals():
    print "\nloading goals\n"


    # These should be getters, not managed in the function.
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

        if player is None:
            bio_id = None
        elif player in bios:
            bio_id = bios[player]
        else:
            print player
            bio_id = Bio.objects.find(player).id
            bios[player] = bio_id
        
        ogplayer = goal.get('own_goal_player')
        if ogplayer is None:
            ogbio_id = None
        elif ogplayer in bios:
            ogbio_id = bios[ogplayer]
        else:
            print ogplayer
            ogbio_id = Bio.objects.find(ogplayer).id
            bios[ogplayer] = ogbio_id

        # Coerce to date to match dict.
        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)
        game_key = (team_id, d)

        if game_key in games:
            game_id = games[game_key]
        else:
            game_id = None
            print "No game match for %s" % goal

        if game_id:
            """
            if bio_id:
                player = Bio.objects.get(id=bio_id)
            else:
                player = None

            if ogbio_id:
                ogplayer = Bio.objects.get(id=ogbio_id)
            else:
                ogplayer = None
                """
                

            return {
                'date': goal['date'],
                'minute': goal['minute'],
                'team_id': team_id, #Team.objects.get(id=team_id),
                'team_original_name': '',

                'player_id': bio_id, #player,
                'own_goal_player_id': ogbio_id,

                'game_id': game_id, #Game.objects.get(id=game_id),

                'own_goal': goal.get('own_goal', False),
                'penalty': goal.get('penalty', False),
                }

    goals = []
    for goal in soccer_db.goals.find():
        g = create_goal(goal)
        if g:
            goals.append(g)
            #Goal.objects.create(**g)

    insert_sql('goals_goal', goals)



@timer
@transaction.commit_on_success
def load_stats():
    # Stats takes forever.

    print "\nloading stats\n"

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    competition_getter = make_competition_getter()
    season_getter = make_season_getter()
    source_getter = make_source_getter()

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

        if stat.get('source'):
            source_id = source_getter(stat['source'])

        else:
            source_id = None

        def c2i(key):
            # Coerce an integer
            if stat.get(key):
                if type(stat[key]) != int:
                    import pdb; pdb.set_trace()
                return stat[key]

            else:
                return None

        l.append({
            'player_id': bio_id,
            'team_id': team_id,
            'competition_id': competition_id,
            'season_id': season_id,
            'games_started': c2i('games_started'),
            'games_played': c2i('games_played'),
            'minutes': c2i('minutes'),
            'goals': c2i('goals'),
            'assists': c2i('assists'),
            'shots': c2i('shots'),
            'shots_on_goal': c2i('shots_on_goal'),
            'fouls_committed': c2i('fouls_committed'),
            'fouls_suffered': c2i('fouls_suffered'),
            'yellow_cards': c2i('yellow_cards'),
            'red_cards': c2i('red_cards'),
            'source_id': source_id,
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

    birthdate_dict = dict(Bio.objects.exclude(birthdate=None).values_list("id", "birthdate"))

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

        bd = birthdate_dict.get(player_id)
        if a['date'] and bd:
            # Coerce bd from datetime.date to datetime.time
            bdt = datetime.datetime.combine(bd, datetime.time())
            age = (a['date'] - bdt).days / 365.25
        else:
            age = None

        if a['on'] is not None and a['off'] is not None:
            try:
                minutes = int(a['off']) - int(a['on'])
            except:
                print "Fail on %s" % str(a)
                minutes = None
        else:
            minutes = None

        result = a.get('result') or ''


        return {
            'team_id': team_id,
            'game_id': game_id,
            'player_id': player_id,
            'on': a['on'],
            'off': a['off'],
            #'team_original_name': '',
            'age': age,
            'minutes': minutes,
            'goals_for': a['goals_for'],
            'goals_against': a['goals_against'],
            'result': result,
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
