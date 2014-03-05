from collections import Counter, defaultdict
import datetime
import os
import pymongo
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from awards.models import Award, AwardItem
from bios.models import Bio
from competitions.models import Competition, Season, SuperSeason
from drafts.models import Draft, Pick
from money.models import Salary
from news.models import NewsSource, FeedItem
from places.models import Country, State, City, Stadium, StadiumMap
from positions.models import Position
from sources.models import Source, SourceUrl
from teams.models import Team, TeamAlias


from utils import insert_sql, timer

from getters import *

from guppy import hpy

connection = pymongo.Connection()
soccer_db = connection.soccer

def generate_mongo_indexes():
    soccer_db.games.ensure_index("date")

def load1():

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


    generate_mongo_indexes()



    # Non-game data.
    load_sources()
    load_places()


    # Simple sport data

    load_competitions()
    load_seasons()

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

    load_stadium_maps()


def load2():
    
    load_lineups()



def load3():
    load_game_stats()

def load4():
    load_news();
    # Consider loading stats last so that we can generate 
    load_stats()
    print hpy().heap()

    # Analysis data




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

    sources = defaultdict(dict)
    source_urls = defaultdict(list)
    
    for source in soccer_db.sources.find():
        source.pop('_id')

        d = sources[source['name']]
        d['name'] = source['name']

        if source['author']:
            d['author'] = source['author']

        if source.get('base_url'):
            source_urls[source['name']].append(source['base_url'])

    source_ids = {}

    for source in sources.values():
        s = Source.objects.create(**source)
        source_ids[s.name] = s.id

    for name, surls in source_urls.items():
        sid = source_ids[name]
        for surl in surls:
            SourceUrl.objects.create(**{
                    'source_id': sid,
                    'url': surl,
                    })
        



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
    print "\nloading %s positions\n" % soccer_db.positions.count()
    for position in soccer_db.positions.find():
        position.pop('_id')
        position['team'] = Team.objects.find(position['team'], create=True)
        position['person'] = Bio.objects.find(position['person'])
        Position.objects.create(**position)

@timer
@transaction.commit_on_success
def load_awards():

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

    print "\nloading %s picks\n" % soccer_db.picks.count()
                
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

    source_getter = make_source_getter()

    for e in soccer_db.news.find():
        e.pop('_id')
        #NewsSource.objects.create(**e)
        source_id = source_getter(e.pop('source'))
        e['source_id'] = source_id
        FeedItem.objects.create(**e)



@timer
@transaction.commit_on_success
def load_teams():
    print "loading %s teams" % soccer_db.teams.count()

    cg = make_city_getter()
    names = set()

    for team in soccer_db.teams.find():
        team.pop('_id')

        founded = city = dissolved =None

        slug = slugify(team['name'])
        short_name = team.get('short_name') or team['name']

        if type(team['founded']) == int:
            try:
                founded = datetime.datetime(team['founded'], 1, 1)
            except:
                print "founded out of range %s" % team

        if team['city']:
            city = cg(team['city'])

        if type(team['dissolved']) == int:
            dissolved = datetime.datetime(team['dissolved'] + 1, 1, 1)
            dissolved = dissolved - datetime.timedelta(days=1)

        if team['name'] not in names:

            if team['name'] == 'New York Giants':
                import pdb; pdb.set_trace()

            names.add(team['name'])
            Team.objects.create(**{
                    'name': team['name'],
                    'short_name': short_name,
                    'slug': slug,
                    'founded': founded,
                    'dissolved': dissolved,
                    'city': city,
                    'international': team.get('international', False),
                    })
        else:
            print "duplicate team name"
            print team


    for alias in soccer_db.name_maps.find():
        alias.pop('_id')
        t = Team.objects.find(name=alias['from_name'], create=True)

        TeamAlias.objects.create(**{
                'team': t,
                'name': alias['to_name'],
                'start': alias['start'],
                'end': alias['end'],
                })


@transaction.commit_on_success
def load_competitions():
    print "loading competitions"
    for c in soccer_db.competitions.find():
        c.pop('_id')
        Competition.objects.create(**c)


@transaction.commit_on_success
def load_seasons():
    print "loading seasons"

    #competition_getter = make_competition_getter()

    l = []

    for s in soccer_db.seasons.find():
        #s.pop('_id')
        #competition_id = competition_getter(s['competition'])
        l.append({
                'name': s['name'],
                #'slug': slugify(s['season']),
                #'competition_id': competition_id,
                'order': s['order'],
                'order2': s['order'],
                })



    for ss in l:
        SuperSeason.objects.create(**ss)





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


def load_stadium_maps():
    print("loading stadium maps")

    stadium_getter = make_stadium_getter()
    team_getter = make_team_getter()

    l = []
    for e in soccer_db.stadium_maps.find():
        tid = team_getter(e['team'])
        sid = stadium_getter(e['stadium'])

        l.append({
                'team_id': tid,
                'stadium_id': sid,
                'start': e['start'],
                'end': e['end'],
                })

    for e in l:
        StadiumMap.objects.create(**e)
        
    #insert_sql("places_stadiummap", l)



@timer
@transaction.commit_on_success
def load_standings():
    print "\n loading %s standings\n" % soccer_db.standings.count()

    team_getter = make_team_getter()
    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    # Create final standings from day-to-day standings
    final_standings = set()
    all_standings = set()
    max_game_standings = {}


    l = []
    for standing in soccer_db.standings.find().sort('team', 1):
        standing.pop('_id')
        
        competition_id = competition_getter(standing['competition'])
        season_id = season_getter(standing['season'], competition_id)
        team_id = team_getter(standing['team'])

        group = standing.get('group') or ''
        division = standing.get('division') or ''

        final = standing.get('final', False)


        d = {
                'competition_id': competition_id,
                'season_id': season_id,
                'team_id': team_id,
                'date': standing.get('date'),
                'division': division,
                'group': group,
                'games': standing['games'],
                'goals_for': standing.get('goals_for'),
                'goals_against': standing.get('goals_against'),
                'wins': standing['wins'],
                'shootout_wins': standing['shootout_wins'],
                'losses': standing['losses'],
                'shootout_losses': standing['shootout_losses'],
                'ties': standing['ties'],
                'points': standing.get('points'),
                'final': final,
                'deduction_reason': '',
                }
        l.append(d)

        """
        key = (standing['team'], standing['competition'], standing['season'])

        all_standings.add(key)
        if final:
            final_standings.add(key)

        if key not in max_game_standings or standing['games'] > max_game_standings[key]:
            max_game_standings[key] = d
            """

    insert_sql("standings_standing", l)

    # Handle this somewhere else.
    # Generate appropriate final standings.
    print("Generating final standings.")
    l2 = []
    for key in all_standings - final_standings:
        standing = max_game_standings[key].copy()
        #standing['final'] = True
        #standing['date'] = None
        l2.append(standing)

    insert_sql("standings_standing", l2)


@timer
@transaction.commit_on_success
def load_bios():
    print("loading bios")

    cg = make_city_getter()


    # Find which names are used so we can only load these bios.
    # Huh? This is unnecessary.
    #fields = [('lineups', 'name'), ('goals', 'goal'), ('stats', 'name'), ('awards', 'recipient'), ('picks', 'text')]
    #names = set()

    # Add names to names field where they have been used.
    #for coll, key in fields:
    #    names.update([e[key] for e in soccer_db[coll].find()])

    # Load bios.
    for bio in soccer_db.bios.find().sort('name', 1):

        #if bio['name'] not in names:
            #print "Skipping %s" % bio['name']
        #    continue

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

        # Having unexpected problems here...
        bd['hall_of_fame'] = bio.get('hall_of_fame')
        if bd['hall_of_fame'] not in (True, False):
            bd['hall_of_fame'] = False

        Bio.objects.create(**bd)

    bio_getter = make_bio_getter()
    bio_ct_id = ContentType.objects.get(app_label='bios', model='bio').id

    images = []
    for bio in soccer_db.bios.find().sort('name', 1):
        if bio.get('img'):
            bid = bio_getter(bio['name'])
            fn = bio['img'].rsplit('/')[-1]
            
            images.append({
                    'filename': fn,
                    'content_type_id': bio_ct_id,
                    'object_id': bid,
                    })

    insert_sql("images_image", images)



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
            season=unicode(e['year']).strip()
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

    season_getter = make_season_getter()

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

        #season_id = Season.objects.find(game['season'], competition_id).id # this!!
        season_id = season_getter(game['season'], competition_id)

        if game['season'] is None:
            import pdb; pdb.set_trace()

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
        not_played = game.get('not_played') or False
        forfeit = game.get('forfeit') or False
        minigame = game.get('minigame') or False
        indoor = game.get('indoor') or False

        minutes = game.get('minutes') or 90

        neutral = game.get('neutral') or False
        attendance = game.get('attendance')

        rnd = game.get('round') or ''
        group = game.get('group') or ''

        # There are lots of problems with the NASL games, 
        # And probably ASL as well. Need to spend a couple
        # of hours repairing those schedules.

        if game['shootout_winner']:
            shootout_winner = team_getter(game['shootout_winner'])
        else:
            shootout_winner = None

        location = game.get('location', '')

        location = location or ''


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
                'not_played': not_played,
                'forfeit': forfeit,

                'goals': goals,
                'minigame': minigame,
                'indoor': indoor,

                'minutes': minutes,
                'competition_id': competition_id,
                'season_id': season_id,
                'round': rnd,
                'group': group,

                'home_team_id': home_team_id,
                'neutral': neutral,

                'stadium_id': stadium_id,
                'city_id': city_id,
                'country_id': country_id,
                'location': location,
                'notes': game.get('notes', ''),
                'video': game.get('video', ''),
                'attendance': attendance,
                
                'referee_id': referee_id,
                'linesman1_id': linesman1_id,
                'linesman2_id': linesman2_id,
                'linesman3_id': linesman3_id,

                'merges': game['merges'],
                })


    print "Inserting %s games results." % len(games)
    # Broke on massive attendance. 
    # Watch out for crazy integer values.
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

    i = 0 # if no goals.
    goals = []
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 50000 == 0:
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
            #import pdb; pdb.set_trace()
            print "Cannot create assists for %s" % goal
            return []

        seen = set()

        for assister in goal['assists']:
            assist_ids = [bio_getter(e) for e in goal['assists']]
            for i, assist_id in enumerate(assist_ids, start=1):
                if assist_id and assist_id not in seen:
                    seen.add(assist_id)
                    assists.append({
                        'player_id': assist_id,
                        'goal_id': goal_id,
                        'order': i,
                        })

    assists = []

    i = 0
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 50000 == 0:
            print i
        create_assists(goal)

    print i
    print len(assists)
    insert_sql('goals_assist', assists)


@timer
@transaction.commit_on_success
def load_game_stats():
    print "\nloading game stats\n"

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    source_getter = make_source_getter()
    game_getter = make_game_getter()
    game_result_getter = make_game_result_getter()

    birthdate_dict = dict(Bio.objects.exclude(birthdate=None).values_list("id", "birthdate"))
    
    print "\nprocessing"

    l = []    
    i = 0
    for i, stat in enumerate(soccer_db.gstats.find(timeout=False)): # no timeout because this query takes forever.
        if i % 50000 == 0:
            print i

        if stat['player'] == '':
            #import pdb; pdb.set_trace()
            continue

        
        try:
            bio_id = bio_getter(stat['player'])
        except:
            continue

        if bio_id is None:
            continue


        bd = birthdate_dict.get(bio_id)
        if stat['date'] and bd:
            # Coerce bd from datetime.date to datetime.time
            bdt = datetime.datetime.combine(bd, datetime.time())
            age = (stat['date'] - bdt).days / 365.25
        else:
            age = None

        team_id = team_getter(stat['team'])

        game_id = game_getter(team_id, stat['date'])


        result = game_result_getter(team_id, stat['date'])

        if game_id is None or team_id is None:
            continue


        def c2i(key):
            # Coerce an integer

            if key in stat and stat[key] != None:
                if type(stat[key]) != int:
                    import pdb; pdb.set_trace()
                return stat[key]

            elif key in stat and stat[key] == None:
                return 0

            else:
                return None

        l.append({
            'player_id': bio_id,
            'team_id': team_id,
            'game_id': game_id,
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
            'on': c2i('on'),
            'off': c2i('off'),
            'age': age,
            'result': result,
            })

    print i


    insert_sql("stats_gamestat", l)



@timer
@transaction.commit_on_success
def load_stats():
    print "\nloading stats\n"

    @timer
    def f():
        return 


    team_getter, bio_getter, competition_getter, season_getter, source_getter = (
        make_team_getter(), make_bio_getter(), make_competition_getter(), make_season_getter(), make_source_getter(),)
                
    print "\nprocessing\n"

    l = []    
    i = 0
    for i, stat in enumerate(soccer_db.stats.find(timeout=False)): # no timeout because this query takes forever.
        if i % 50000 == 0:
            print i

        if stat['name'] == '':
            #import pdb; pdb.set_trace()
            continue


        team_id = team_getter(stat['team'])
        bio_id = bio_getter(stat['name'])
        competition_id = competition_getter(stat['competition'])
        season_id = season_getter(stat['season'], competition_id)


        # cf game_sources stuff.
        """
        # change to sources!
        if stat.get('sources'): 
            sources = sorted(set(stat.get('sources')))
        elif stat.get('source'):
            sources = [stat['source']]
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
            #t = (game['date'], team1_id, source_id, source_url)
            #stat_sources.append(t)
        """

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

    def create_appearance(a):

        if not a['name']:
            print a
            return None

        team_id = team_getter(a['team'])
        player_id = bio_getter(a['name'])
        game_id = game_getter(team_id, a['date'])

        if not game_id:
            print "Cannot create %s" % a
            return {}

        if a['on'] is not None and a['off'] is not None:
            try:
                minutes = int(a['off']) - int(a['on'])
            except:
                print "Fail on %s" % str(a)
                minutes = None
        else:
            minutes = None

        return {
            'team_id': team_id,
            'game_id': game_id,
            'player_id': player_id,
            'on': a['on'],
            'off': a['off'],
            'minutes': minutes,
            'order': a.get('order', None),
            }

    # Create the appearance objects.
    l = []
    i = 0
    for i, a in enumerate(soccer_db.lineups.find()):
        u = create_appearance(a)
        if u:
            l.append(u)

        if i % 50000 == 0:
            print i

    print i
    print "Creating lineups"
    insert_sql('lineups_appearance', l)




if __name__ == "__main__":
    if sys.argv[1] == '1':
        load1()
    elif sys.argv[1] == '2':
        load2()
    elif sys.argv[1] == '3':
        load3()
    elif sys.argv[1] == '4':
        load4()
    elif sys.argv[1] == '5':
        update()

    else:
        raise
