from collections import defaultdict, Counter
import datetime
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'

from django.db import transaction
from django.db.models import Count

from bios.models import Bio
from competitions.models import Competition, Season
from drafts.models import Draft, Pick
from games.models import Game, GameMinute
from goals.models import Goal
from lineups.models import Appearance
from places.models import Stadium
from positions.models import Position
from sources.models import Source
from standings.models import Standing, StadiumStanding
from stats.models import Stat, CareerStat, CoachStat, GameStat
from teams.models import Team
from utils import insert_sql, timer


# Really need to rethink how generate works.
# Some intermediate models could probably help improve speeds.


@timer
def generate():
    """
    Generate stats.
    """

    # Need to choose one.
    # Generate coaching stats!
    #generate_position_standings()
    #generate_position_stats()


    # This broke unexpectedly for Premier League coach stats.
    generate_coach_stats_for_competitions()

    #generate_game_data_quality()

    set_draft_picks()

    generate_source_data()

    generate_career_stats()
    generate_competition_stats()
    generate_team_stats()
    generate_competition_standings()
    generate_team_standings()
    generate_stadium_standings()
    generate_season_data()

    #generate_player_standings()

    #generate_game_minutes()



@timer
def generate_coach_stats_for_competitions():
    generate_coach_stats('North American Soccer League')
    generate_coach_stats('Major League Soccer')

    generate_coach_stats('North American Soccer League (2011-)')
    generate_coach_stats('USSF Division 2 Professional League')
    generate_coach_stats('USL First Division')
    generate_coach_stats('USL Second Division')
    generate_coach_stats('American Professional Soccer League')

    #generate_coach_stats('Premier League')
    #generate_coach_stats('La Liga')
    #generate_coach_stats('Serie A')

    generate_coach_stats('CONCACAF Champions League')



@timer
@transaction.commit_on_success
def generate_player_standings():
    # Kill this. this is part of game_stat / player_stat now...I think.

    # merge this with plus/minus.

    results = Game.objects.values_list('id', 'team1', 'team1_result', 'team2', 'team2_result')
    result_map = {}
    for gid, t1, t1r, t2, t2r in results:
        result_map[(gid, t1)] = t1r
        result_map[(gid, t2)] = t2r

    players = set()
    standings = defaultdict(int)
    appearances = Appearance.objects.values_list('game', 'team', 'player')
    for game, team, player in appearances:
        result = result_map[(game, team)]
        standings[(player, result)] += 1
        players.add(player)

    for pid in players:
        w, l, t = standings[(pid, 'w')], standings[(pid, 'l')], standings[(pid, 't')]
        if w or l or t:
            try:
                c = CareerStat.objects.get(player=pid)
            except:
                continue
            c.wins, c.losses, c.ties = w, l, t
            c.save()


def set_draft_picks():
    """
    Handle abnormal draft conditions
    """
    # This applies to drafts where a team picked another draft pick, e.g.

    # Not bothering parsing since this has only happened one time.

    try:
        d = Draft.objects.get(competition__slug='major-league-soccer', name='SuperDraft', season__name='2002')
    #except drafts.models.DoesNotExist: 
    except:
        return # haven't loaded draft.
        

    picks = Pick.objects.filter(text__contains='SuperDraft')
    for pick in picks:
        number = int(pick.text.lower().split('pick')[0].strip().replace('#', ''))
        target = Pick.objects.get(draft=d, number=number)
        pick.pick = target
        pick.save()

@timer
def generate_source_data():
    print "Generating source data."
    from games.models import GameSource
    game_counts = Counter([e[0] for e in GameSource.objects.values_list('source')])
    stat_counts = Counter([e[0] for e in Stat.objects.exclude(source=None).values_list('source')])

    for source in Source.objects.all():
        source.games = game_counts[source.id]
        source.stats = stat_counts[source.id]
        source.total = source.games + source.stats
        source.save()
    
        


@timer
@transaction.commit_on_success
def generate_season_data():
    # Generate season data including average age, nationality data (somehow)
    print "Generating season data."

    minutes_dict = defaultdict(int)
    minutes_with_age_dict = defaultdict(int)
    age_minutes_dict = defaultdict(int)

    for season, minutes, age in GameStat.objects.values_list('game__season', 'minutes', 'age'):
        if minutes:
            minutes_dict[season] += minutes
            if age:
                minutes_with_age_dict[season] += minutes
                am = minutes * age
                age_minutes_dict[season] += am
        
    for sid, minutes in minutes_dict.items():
        minutes_with_age = minutes_with_age_dict[sid]
        age_minutes = age_minutes_dict[sid]

        #print 'Setting season %s' % sid        
        s = Season.objects.get(id=sid)
        s.minutes = minutes
        s.minutes_with_age = minutes_with_age
        s.age_minutes = age_minutes
        s.save()

    
    """

        from lineups.models import Appearance
        appearances = Appearance.objects.filter(game__season=self)
        if not appearances.exists():
            return {}
        else:
            minutes_with_age = 0
            age_minutes = 0
            age_bucket_minutes = defaultdict(int)
            nationality_minutes = defaultdict(int)
            
            for appearance in appearances:
                if appearance.age:
                    minutes_with_age += appearance.minutes
                    age_minutes += appearance.age * appearance.minutes
                    age_bucket_minutes[int(appearance.age)] += appearance.minutes

                bp = appearance.player.birthplace
                if bp and bp.country:
                    nationality_minutes[bp.country] += appearance.minutes

            return {
                'minutes_with_age': minutes_with_age,
                'age_minutes': age_minutes,
                'age_bucket_minutes': age_bucket_minutes,
                'nationality_minutes': nationality_minutes,
                }

             """


def calculate_standings(team, games=None):
    # Do this with a dict, not a game object.

    if games is None:
        games = Game.objects.team_filter(position.team)

    wins = losses = ties = 0
    for game in games:
        r = game.result(team)

        if r == 'w':
            wins += 1
        elif r == 'l':
            losses += 1
        elif r == 't':
            ties += 1

    return wins, losses, ties

            
    
@timer
@transaction.commit_on_success
def generate_game_data_quality():
    """
    Generate game data quality info.
    """
    print "Quality data for all games."


    global_starters = Appearance.objects.filter(on=0).exclude(off=0)

    starter_map = Counter([e[0] for e in global_starters.values_list('game')])
    goal_map = Counter([e[0] for e in Goal.objects.values_list('game')])

    for game in Game.objects.all():
        game.starter_count = starter_map.get(game.id, 0)
        game.goal_count = goal_map.get(game.id, 0)
        game.save()
    

@transaction.commit_on_success
def generate_stats_generic(table, qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """

    #print "Merging stats."
    final_dict = {}

    # Don't try to add these items.
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id', 'source_id')


    for stat in qs.values():

        # Set unaddable values to none.
        for k,v  in stat.items():
            if v in ('?', 'None', '-'):
                stat[k] = None



        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']
        key = make_key(stat) 
        # Create a new entry for this stat type
        if key not in final_dict:
            # This should set all necessary fields.
            final_dict[key] = stat
        else:
            # 
            d = final_dict[key]
            for key, value in stat.items():
                if key not in excluded: 
                    if not d[key]:
                        d[key] = value
                    else:
                        if value:
                            try:
                                d[key] += value
                            except:
                                import pdb; pdb.set_trace()
                                x = 5


    for key, stat in final_dict.items():
        stat.pop('id')
        for e in update_dict.keys():
            if e in stat:
                stat.pop(e)
        
        # update_dict seems unnecessary at this point. Those values aren't in the given stat.
        #stat.update(update_dict)

    insert_sql(table, final_dict.values())
    #insert_sql("stats_stat", final_dict.values())
        #Stat.objects.create(**stat)


@timer
def generate_career_stats():
    """
    Generate career stats for all players,
    generate from individual stat objects.
    """
    # Need to exclude indoor stats from career stats.
    print "generating career stats"
    make_key = lambda s: s['player_id']
    update = {
        'team_id': None,
        'competition_id': None,
        'season_id': None,
        }
    
    #generate_stats_generic("stats_careerstat", Stat.objects.filter(competition__code='soccer'), make_key, update)    
    generate_stats_generic("stats_careerstat", Stat.objects.all(), make_key, update)    
    #generate_career_plus_minus()
        
@timer
def generate_team_stats():
    print "generating team stats"
    for team in Team.objects.all():
        stats = Stat.objects.filter(team=team)
        make_key = lambda s: (s['player_id'], s['team_id'])
        update = {'competition_id': None, 'season_id': None }
        generate_stats_generic('stats_teamstat', stats, make_key, update)


@timer
def generate_competition_stats():
    print "generating competition stats"
    for competition in Competition.objects.all():
        stats = Stat.objects.filter(competition=competition)
        make_key = lambda s: (s['player_id'], s['competition_id'])
        update = {'team_id': None, 'season_id': None }
        generate_stats_generic('stats_competitionstat', stats, make_key, update)


#############
### Standings 
#############

@transaction.commit_on_success
def generate_standings_generic(qs, make_key, update_dict):
    """
    Used to generate different kinds of standings.
    Currently: team standings and career standings
    """

    final_dict = {} # Used to record final standings.
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id', 'division', 'group')
    
    # Don't include rolling standings.
    final_qs = qs.filter(final=True)

    for standing in final_qs.values():
        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']

        for k,v  in standing.items():
            if v == 'None':
                standing[k] = None

        key = make_key(standing) 
        if key not in final_dict:
            # This should set all necessary fields.
            final_dict[key] = standing
        else:
            d = final_dict[key]
            for key, value in standing.items():
                if key not in excluded:
                    if not d[key]:
                        d[key] = value
                    else:
                        # Check for None values.
                        if value:
                            try:
                                d[key] += value
                            except:
                                import pdb; pdb.set_trace()
                                x = 5

    for key, standing in final_dict.items():
        standing.pop('id')
        standing.update(update_dict)
        s = Standing.objects.create(**standing)



@timer
def generate_competition_standings():
    """
    Generate all-time standings for each competition.
    """
    # Broken?

    print "generating competition standings"
    for competition in Competition.objects.all():
        standings = Standing.objects.filter(competition=competition).exclude(season=None)
        make_key = lambda s: (s['team_id'], s['competition_id'])
        update = {'season_id': None }
        generate_standings_generic(standings, make_key, update)




@timer
def generate_team_standings():
    print "generating team standings"
    for team in Team.objects.all():
        standings = Standing.objects.filter(team=team).exclude(season=None)
        make_key = lambda s: s['team_id']
        update = {'season_id': None, 'competition_id': None }
        generate_standings_generic(standings, make_key, update)


@timer
def generate_stadium_standings():
    standings = {}

    def update_standing(game, team, stadium):
        key = (stadium, team)
        if key not in standings:
            standings[key] = {
                'team': team,
                'stadium': stadium,
                'games': 0,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'goals_for': 0,
                'goals_against': 0,
                }

        if team == game.team1:
            result = game.team1_result
            gf, ga = game.team1_score, game.team2_score
        elif team == game.team2:
            result = game.team2_result
            gf, ga = game.team2_score, game.team1_score
        else:
            import pdb; pdb.set_trace()

        if not result:
            return

        s = standings[key]

        s['games'] += 1

        if result == 'w':
            s['wins'] += 1
        elif result == 't':
            s['ties'] += 1
        elif result == 'l':
            s['losses'] += 1
        else:
            import pdb; pdb.set_trace()

        if gf:
            s['goals_for'] += gf
        if ga:
            s['goals_against'] += ga


    for stadium in Stadium.objects.all():
        games = Game.objects.filter(stadium=stadium)

        for game in games:
            update_standing(game, game.team1, stadium)
            update_standing(game, game.team2, stadium)

    for e in standings.values():
        StadiumStanding.objects.create(**e)
        

@timer
def generate_position_standings():
    """Generate standings for all positions."""
    print "Calculating standings for positions."
    Position.objects.generate_standings()





def make_position_date_getter():
    positions = Position.objects.values_list('person', 'team', 'name', 'start', 'end')
    pm = defaultdict(list)

    for person, team, name, start, end in positions:
        l = pm[team]
        if end is None:
            end = datetime.date.today()

        if start is None:
            continue

        t = (person, name, start, end)
        l.append(t)
        
        
    
    def position_getter(team, date):
        l = pm[team]
        return [e[0] for e in l if e[2] <= date and e[3] >= date]

    return position_getter


def generate_coach_stats(competition):

    def update_stat(game_data, person, team, season):

        date, season, t1, t2, t1s, t2s, t1r, t2r = game_data

        # Short circuit if game doesn't have a result.
        if not t1r and not t2r:
            return 


        key = (person, team, season)
        if key not in coach_stats:
            coach_stats[key] = {
                'person_id': person,
                'team_id': team,
                'competition_id': c.id,
                'season_id': season,
                'plus_minus': 0,
                'goals_for': 0,
                'goals_against': 0,
                'games': 0,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                }
            
        if team == t1:
            try:
                gd = t1s - t2s
            except:
                import pdb; pdb.set_trace()

            gf, ga = t1s, t2s
            result = t1r
        elif team == t2:
            gd = t2s - t1s
            gf, ga = t2s, t1s
            result = t2r
        else:
            import pdb; pdb.set_trace()

        cs = coach_stats[key]
        cs['plus_minus'] += gd
        cs['goals_for'] += gf
        cs['goals_against'] += ga
        cs['games'] += 1
        if result == 't':
            cs['ties'] += 1
        elif result == 'w':
            cs['wins'] += 1
        elif result == 'l':
            cs['losses'] += 1
        else:
            import pdb; pdb.set_trace()


    c = Competition.objects.get(name=competition)
    coach_stats = {}

    games = Game.objects.filter(competition=c).values_list('date', 'season', 'team1', 'team2', 'team1_score', 'team2_score', 'team1_result', 'team2_result')
    pdg = make_position_date_getter()

    for game_data in games:
        date, season, t1, t2 = game_data[:4]

        positions1 = pdg(t1, date)
        for person in positions1:
            update_stat(game_data, person, t1, season)

        positions2 = pdg(t2, date)
        for person in positions2:
            update_stat(game_data, person, t2, season)

    #insert_sql('"stats_coachstat', coach_stats.values())
    for e in coach_stats.values():
        CoachStat.objects.create(**e)
    #x = 5

    

@timer
@transaction.commit_on_success
def generate_position_stats():
    # Generate stats for non-players. Coaches, Owners, etc.
    # Need to start by initializing a list of all games.

    for position in Position.objects.order_by('person'):
        if position.end is None:
            end = datetime.date.today()
        else:
            end = position.end

        if position.start:
            games = Game.objects.team_filter(position.team).filter(date__gte=position.start, date__lte=end)
            if games.exists():
                try:
                    print "Creating result stats for %s games for %s - %s at %s" % (games.count(), position.person, position.name, position.team)
                except:
                    print "Creating result stats."
                position.wins, position.losses, position.ties = calculate_standings(position.team, games)
                position.save()
        



def generate_plus_minus(appearance_qs):
    """
    Generate the +/- for a given queryset.
    """

    print "Generating plus_minus"
    d = defaultdict(int)

    for (i, a) in enumerate(appearance_qs.values()):
        if i % 1000 == 0:
            print i

        try:
            key = a['player_id']
        except:
            import pdb; pdb.set_trace()
        try:
            d[key] += a['goals_for'] - a['goals_against']
        except:
            "Cannot get +/- for %s" % a
    return d


@transaction.commit_on_success
def generate_career_plus_minus():
    print "generating career plus minus"
    plus_minus = generate_plus_minus(Appearance.objects.all())
    career_stat_dict = Stat.career_stats.to_dict()

    for i, (k, v) in enumerate(plus_minus.items()):
        if i % 100 == 0:
            print i
        s = career_stat_dict[k]
        s.plus_minus = v
        s.save()


@transaction.commit_on_success
def generate_season_plus_minus():
    competition_slugs = ['major-league-soccer']
    #competition_slugs = ['mls-reserve-league']

    d = {}

    for slug in competition_slugs:
        c = Competition.objects.get(slug=slug)
        for season in c.season_set.all():
            #import pdb; pdb.set_trace()
            appearances = Appearance.objects.filter(game__season=season)
            team_ids = set([e[0] for e in appearances.values_list('team')])
            for team_id in team_ids:
                team_appearances = appearances.filter(team=team_id)
                pms = generate_plus_minus(team_appearances)
                for pid, pm in pms.items():
                    key = (pid, team_id, season.id)
                    d[key] = pm
                
    return d


@timer
@transaction.commit_on_success
def generate_game_minutes():
    """
    Generate all game minutes that we can.
    These are single minute slices of a game.
    Really intensive cpu use.
    """
    print "Generating game minutes"
    # Possibly use game stat objects.


    l = []
    print "Creating score for %s games" % Game.objects.count()
    for i, e in enumerate(Game.objects.all()):
        if i % 1000 == 0:
            print "Making scores for %s" % i
        
        l.extend(e.game_scores_by_minute())

    # Just want to know how long this takes.
    @timer
    def insert_game_minutes():
        print "Generating %s game minutes" % len(l)
        insert_sql("games_gameminute", l)

    insert_game_minutes()



def generate_top_attendances(qs=None):
    """
    Generate a rolling list of top attendances.
    """
    # Put this in GameManager?

    if qs is None:
        qs = Game.objects.all()

    qs = qs.order_by('date')
    
    max = -1

    gids = []

    for gid, attendance in qs.values_list("id", "attendance"):
        if gid in (7591, 8202, 8184, 11119, 8671, 3809):
            continue

        if attendance:
            if attendance > max:
                max = attendance
                gids.append(gid)

    return Game.objects.filter(id__in=gids).order_by('date')
    
            
                        
if __name__ == "__main__":
    generate()


