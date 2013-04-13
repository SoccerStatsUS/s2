import datetime
import os
import pymongo

os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'

from django.contrib.contenttypes.models import ContentType
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
from places.models import Country, State, City, Stadium, Country
from positions.models import Position
from sources.models import Source
from stats.models import Stat
from standings.models import Standing
from teams.models import Team, TeamAlias

from utils import insert_sql, timer

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

    game_team_map = Game.objects.game_dict()

    def getter(team_id, dt):

        # This is becoming a larger and larger problem.
        # Going to have to reconsider how we label games because of dateless games.

        if dt is None:
            print "Failed to find game for team %s on %s" % (team_id, dt)
            gid = None
        else:
            # Not doing full game times yet...
            dx = datetime.date(dt.year, dt.month, dt.day) # Avoid datetime.date/datetime.datetime mismatch.
            key = (team_id, dx)
            if key in game_team_map:
                gid = game_team_map[key]
            else:
                print "Failed to find game for team %s on %s" % (team_id, dx)
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


    # Simple sport data
    load_competitions()
    load_teams()
    load_standings()

    load_bios()
    load_salaries()

    load_stadiums()

    # List data
    # Put this before standings?
    load_awards()
    load_drafts()
    load_positions()

    # Complex game data
    load_games()

    load_goals()
    load_assists()
    load_lineups()

    # Consider loading stats last so that we can generate 
    load_stats()

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
        #source['games'] = source['stats'] = 0
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

    city_set = set()

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
        Position.objects.create(**position)

@timer
@transaction.commit_on_success
def load_awards():
    print
    print "\nloading awards\n"
    awards = set()
    award_dict = {}


    competition_getter = make_competition_getter()
    season_getter = make_season_getter()
    team_getter = make_team_getter()
    bio_getter = make_bio_getter()

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


    bio_ct_id = ContentType.objects.get(app_label='bios', model='bio').id
    team_ct_id = ContentType.objects.get(app_label='teams', model='team').id

    # Create awardItems.
    items = []
    for item in soccer_db.awards.find().sort('recipient', 1):
        item.pop('_id')

        # So we can have a season, a year, both, or neither for an award item
        award = award_dict[(item['competition'], item['award'], item.get('type', ''))]
        award_id = award.id

        # NCAA seasons don't exist.
        # Would be good to use get otherwise to ensure we have good data.
        if award.competition:
            competition_id = award.competition.id
            season_id = season_getter(item['season'], competition_id)
        else:
            season_id = None

        model_name = item.pop('model')
        if model_name == 'Bio':
            content_type_id = bio_ct_id
            object_id = bio_getter(item['recipient'])
        elif model_name == 'Team':
            content_type_id = team_ct_id
            object_id = team_getter(item['recipient'])
        else:
            import pdb; pdb.set_trace()
            raise

        items.append({
                'award_id': award_id,
                'season_id': season_id,
                'content_type_id': content_type_id,
                'object_id': object_id,
                })

    insert_sql("awards_awarditem", items)


@timer
@transaction.commit_on_success
def load_drafts():
    print "\nloading drafts\n"

    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    team_getter = make_team_getter()

    # Create the set of drafts.

    for draft in soccer_db.drafts.find().sort('team', 1):
        draft.pop('_id')

        if draft['competition']:
            competition_id = competition_getter(draft['competition'])        
        else:
            competition_id = None

        season_id = season_getter(draft['season'], competition_id)

        Draft.objects.create(**{
                'name': draft['name'],
                'season_id': season_id,
                'competition_id': competition_id,
                'start': draft.get('start'),
                'end': draft.get('end'),
                })
                
    # Create picks
    picks = []
    for pick in soccer_db.picks.find():

        # draft, text, player, position, team

        c = pick.get('competition')
        if c:
            competition_id = competition_getter(pick.get('competition'))
        else:
            competition_id = None

        season_id = season_getter(pick.get('season'), competition_id)
        draft = Draft.objects.get(name=pick.get('draft'), competition_id=competition_id, season_id=season_id)

        if pick['team'] == 'Sean_Irish_LAGalaxy/Geneva':
            pass #import pdb; pdb.set_trace()


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

    insert_sql("drafts_pick", picks)
        
        
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

    cg = make_city_getter()


    names = set()

    for team in soccer_db.teams.find():
        team.pop('_id')

        if type(team['founded']) == int:
            try:
                founded = datetime.datetime(team['founded'], 1, 1)
            except:
                print "founded out of range %s" % team
                founded = None
            team['founded'] = founded


        if team['city']:
            team['city'] = cg(team['city'])
        else:
            team['city'] = None

        if type(team['dissolved']) == int:
            dissolved = datetime.datetime(team['dissolved'] + 1, 1, 1)
            dissolved = dissolved - datetime.timedelta(days=1)
            team['dissolved'] = dissolved

        team['slug'] = slugify(team['name'])

        team['short_name'] = team.get('short_name') or team['name']


        if 'abbreviation' in team:
            team.pop('abbreviation')

        if 'parent' in team:
            team.pop('parent')

        if 'next' in team:
            team.pop('next')
        if 'country' in team:
            team.pop('country')
            


        if team['name'] in names:
            print "duplicate team name"
            print team
        else:
            names.add(team['name'])
            Team.objects.create(**team)

    for alias in soccer_db.name_maps.find():
        alias.pop('_id')
        team = Team.objects.find(name=alias['from_name'], create=True)

        TeamAlias.objects.create(**{
                'team': team,
                'name': alias['to_name'],
                'start': alias['start'],
                'end': alias['end'],
                })


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

@timer
@transaction.commit_on_success
def load_stadiums():
    print "loading stadiums"

    cg = make_city_getter()

    for stadium in soccer_db.stadiums.find():
        stadium.pop('_id')
        stadium['slug'] = slugify(stadium['name'])

        try:
            stadium['city'] = cg(stadium['location'])
        except:
            import pdb; pdb.set_trace()

        
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
    # Low-hanging fruit. Please speed this up soon.

    team_getter = make_team_getter()
    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    l = []
    for standing in soccer_db.standings.find().sort('team', 1):
        standing.pop('_id')
        
        if standing['season'] == None:
            import pdb; pdb.set_trace()

        competition_id = competition_getter(standing['competition'])
        season_id = season_getter(standing['season'], competition_id)
        team_id = team_getter(standing['team'])

        group = standing.get('group') or ''
        division = standing.get('division') or ''

        final = standing.get('final', False)

        l.append({
                'competition_id': competition_id,
                'season_id': season_id,
                'team_id': team_id,
                'date': standing.get('date'),
                'division': division,
                'group': group,
                'games': standing['games'],
                'goals_for': standing['goals_for'],
                'goals_against': standing['goals_against'],
                'wins': standing['wins'],
                'shootout_wins': standing['shootout_wins'],
                'losses': standing['losses'],
                'shootout_losses': standing['shootout_losses'],
                'ties': standing['ties'],
                'points': standing.get('points'),
                'final': final,
                'deduction_reason': '',
                })

    insert_sql("standings_standing", l)

@timer
@transaction.commit_on_success
def load_bios():
    cg = make_city_getter()


    # Find which names are used so we can only load these bios.
    fields = [('lineups', 'name'), ('goals', 'goal'), ('stats', 'name'), ('awards', 'recipient'), ('picks', 'text')]
    names = set()

    # Add names to names field where they have been used.
    for coll, key in fields:
        names.update([e[key] for e in soccer_db[coll].find()])

    # Load bios.
    for bio in soccer_db.bios.find().sort('name', 1):

        if bio['name'] not in names:
            #print "Skipping %s" % bio['name']
            continue


        #try:
        #    print "Creating bio for %s" % bio['name']
        #except:
        #    print "Created bio."

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
    print "\n loading %s games\n" % soccer_db.games.count()

    stadium_getter = make_stadium_getter()
    team_getter = make_team_getter()
    competition_getter = make_competition_getter()    
    source_getter = make_source_getter()
    bio_getter = make_bio_getter()

    city_getter = make_city_getter()
    country_getter = make_country_getter()

    games = []
    game_sources = []

    for game in soccer_db.games.find().sort('date', 1):

        # Apply stadium / state / country information.
        
        stadium_id = city_id = country_id = None
        if game.get('stadium'):
            stadium_id = stadium_getter(game['stadium'])
            s = Stadium.objects.get(id=stadium_id)
            if s.city:
                city_id = s.city.id
            else:
                city_id = None

        elif game.get('city'):
            city_id = city_getter(game['city']).id

        elif game.get('location'):

            country_id = country_getter(game['location'])
            if country_id is None:
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
            referee_id = bio_getter(game['referee'])

        if game.get('linesman1'):
            linesman1_id = bio_getter(game['linesman1'])

        if game.get('linesman2'):
            linesman2_id = bio_getter(game['linesman2'])

        if game.get('linesman3'):
            linesman3_id = bio_getter(game['linesman3'])


        if game.get('sources'):
            sources = sorted(set(game.get('sources')))
        elif game.get('source'):
            sources = [game['source']]
        else:
            sources = []

        
        for source in sources:
            if source.strip() == '':
                continue
            elif source.startswith('http'):
                source_url = source
            else:
                source_url = ''
            source_id = source_getter(source)
            t = (game['date'], team1_id, source_id, source_url)
            game_sources.append(t)

        result_unknown = game.get('result_unknown') or False
        played = game.get('played') or True
        forfeit = game.get('forfeit') or False
        minigame = game.get('minigame') or False

        minutes = game.get('minutes') or 90

        neutral = game.get('neutral') or False
        attendance = game.get('attendance')

        r = game.get('round') or ''

        # There are lots of problems with the NASL games, 
        # And probably ASL as well. Need to spend a couple
        # of hours repairing those schedules.

        if game['shootout_winner']:
            shootout_winner = team_getter(game['shootout_winner'])
        else:
            shootout_winner = None


        games.append({
                'date': game['date'],
                'has_date': bool(game['date']),

                'team1_id': team1_id,
                'team1_original_name': game['team1_original_name'],
                'team2_id': team2_id,
                'team2_original_name': game['team2_original_name'],

                'team1_score': game['team1_score'],
                'official_team1_score': game.get('official_team1_score'),
                'team2_score': game['team2_score'],
                'official_team2_score': game.get('official_team2_score'),

                'shootout_winner_id': shootout_winner,

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
                'round': r,

                'home_team_id': home_team_id,
                'neutral': neutral,

                'stadium_id': stadium_id,
                'city_id': city_id,
                'country_id': country_id,
                'location': game.get('location', ''),
                'notes': game.get('notes', ''),
                'video': game.get('video', ''),
                'attendance': attendance,
                
                'referee_id': referee_id,
                'linesman1_id': linesman1_id,
                'linesman2_id': linesman2_id,
                'linesman3_id': linesman3_id,
                })



    print "Inserting games results."
    insert_sql("games_game", games)

    print "Inserting games sources."
    game_getter = make_game_getter()
    
    l = []
    for date, team_id, source_id, source_url in game_sources:

        # Don't call game_getter without date. Need to give games unique id's.
        if date:
            game_id = game_getter(team_id, date)
            if game_id:
                l.append({
                        'game_id': game_id,
                        'source_id': source_id,
                        'source_url': source_url,
                        })

    insert_sql("games_gamesource", l)
            



@timer
@transaction.commit_on_success
def load_goals():
    print "\nloading goals\n"

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    game_getter = make_game_getter()

    l = []

    def create_goal(goal):

        team_id = team_getter(goal['team'])
        bio_id = ogbio_id = None

        if goal['goal']:
            bio_id = bio_getter(goal['goal'])

        if goal.get('own_goal_player'):
            ogbio_id = bio_getter(goal['own_goal_player'])


        # Tough to apply a goal without a date...
        if not goal['date']:
            return {}

        # Coerce to date to match dict.
        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)
        game_id = game_getter(team_id, d)
        if not game_id:
            print "Cannot create %s" % goal
            return {}
        else:
            return {
                'date': goal['date'],
                'minute': goal['minute'],
                'team_id': team_id, 
                #'team_original_name': '',

                'player_id': bio_id, #player,
                'own_goal_player_id': ogbio_id,

                'game_id': game_id, 

                'own_goal': goal.get('own_goal', False),
                'penalty': goal.get('penalty', False),
                }

                                

    goals = []

    i = 0
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 5000 == 0:
            print i

        g = create_goal(goal)
        if g:
            goals.append(g)

    
    print i

    insert_sql('goals_goal', goals)
        
@timer
@transaction.commit_on_success
def load_assists():
    print "\nloading assists\n"

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    goal_getter = make_goal_getter()

    def create_assists(goal):
        if not goal['assists']:
            return []

        if goal['assists'] == ['']:
            return []

        team_id = team_getter(goal['team'])
        bio_id = ogbio_id = None

        if goal['goal']:
            bio_id = bio_getter(goal['goal'])


        if not goal['date']:
            return {}

        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)

        goal_id = goal_getter(team_id, bio_id, goal['minute'], d)
        if not goal_id:
            print "Cannot create assists for %s" % goal
            return []

        for assister in goal['assists']:
            assist_ids = [bio_getter(e) for e in goal['assists']]
            for i, assist_id in enumerate(assist_ids, start=1):
                if assist_id:
                    assists.append({
                        'player_id': assist_id,
                        'goal_id': goal_id,
                        'order': i,
                        })

    assists = []

    i = 0
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 5000 == 0:
            print i
        create_assists(goal)

    print i

    insert_sql('goals_assist', assists)




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
    i = 0
    for i, stat in enumerate(soccer_db.stats.find(timeout=False)): # no timeout because this query takes forever.
        if i % 5000 == 0:
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

            if key in stat and stat[key] != None:
                if type(stat[key]) != int:
                    import pdb; pdb.set_trace()
                return stat[key]

            #elif key in stat:
            #    import pdb; pdb.set_trace()

            elif key in stat and stat[key] == None:
                return 0

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

    print i

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
            'order': a.get('order', None),
            }

    # Create the appearance objects.
    l = []
    i = 0
    for i, a in enumerate(soccer_db.lineups.find()):
        u = create_appearance(a)
        if u:
            l.append(u)

        if i % 5000 == 0:
            print i

    print i

    print "Creating appearances"

    insert_sql('lineups_appearance', l)
