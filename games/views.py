import datetime

from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from competitions.models import Competition
from games.models import Game, GameSource
from goals.models import Goal
from standings.models import Standing
from stats.models import Stat, CareerStat
from teams.models import Team

from collections import defaultdict, Counter
import json


def homepage(request):

    try:
        mls = Competition.objects.get(slug='major-league-soccer')
    except:
        mls = None

    context = {
        'mls': mls,
        }

    return render_to_response("homepage.html",
                              context,
                              context_instance=RequestContext(request))
        


@cache_page(60 * 60 * 12)
def homepage_old(request):
    """
    The site homepage. Currently badly underperfoming.
    """

    # Homepage fixes.
    # Shrink the size of the On This Day Box, move lower.
    # Add Standings.
    # Add tab for games from different competitions.
    # Add News
    # Add detailed links to different parts of the website.

    # What are the cool things you can get on the site?
    # Player +/-
    # Manager details
    # Career stats
    # Stats across competitions
    # Breadcrumbs?

    today = datetime.date.today()

    game_leaders = CareerStat.objects.exclude(games_played=None).order_by('-games_played')[:10]
    goal_leaders = CareerStat.objects.exclude(goals=None).order_by('-goals')[:10]

    recent_games = Game.objects.exclude(date=None).filter(date__lt=today).exclude(team1_result='').order_by('-date')[:10]

    goals = Goal.objects.count()


    try:
        mls_game = Game.objects.filter(competition__slug='major-league-soccer').order_by('date')[0]
    except:
        mls_game = None

    try:
        oc_game = Game.objects.get(competition__slug='us-open-cup', season__name='1924', round='f')
    except:
        oc_game = None

    context = {
        'today': today,
        'born': Bio.objects.born_on(today.month, today.day),
        'games': recent_games,
        'standings': Standing.objects.filter(season__competition__slug='major-league-soccer').count(), 
        'game_leaders': game_leaders,
        'goal_leaders': goal_leaders,
        'game_count': Game.objects.count(),
        'bio_count': Bio.objects.count(),
        'team_count': Team.objects.count(),
        'competition_count': Competition.objects.count(),

        'mls_game': mls_game,
        'oc_game': oc_game,
        
        }
    return render_to_response("homepage.html",
                              context,
                              context_instance=RequestContext(request))

def bad_games(request):
    
    context = {
        'duplicate_games': Game.objects.duplicate_games(),
        }

    return render_to_response("games/bad.html",
                              context,
                              context_instance=RequestContext(request)
                              )    

    

def games_index(request):
    # Add a paginator.
    # This is probably unnecesary.
    # Consider turning into a games analysis page.
    # Home/Away advantage, graphs, etc.
    
    games = Game.objects.order_by("-date").exclude(date=None)
    game_count = games.count()

    by_year = Counter([e.year for e in games.values_list('date', flat=True)])

    #gd = defaultdict(int)
    #ceiling = 8
    #for game in games.exclude(home_team=None).exclude(team1_score=None).exclude(team2_score=None):
    #    gd[(min(game.home_score(), ceiling), min(game.away_score(), ceiling))] += 1

    context = {
        'games': games,
        'game_count': game_count,
        'games_by_year': json.dumps(sorted(by_year.items())),
        'goal_distribution': json.dumps(gd),
        }

    return render_to_response("games/index.html",
                              context,
                              context_instance=RequestContext(request))

    """
    attendance_game_count = 0
    total_attendance = 0

    month_dict = defaultdict(int)
    team_dict = defaultdict(int)
    result_dict = defaultdict(int)

    game_year_dict = defaultdict(int)
    attendance_year_dict = defaultdict(int)

    # Pull this out.
    for date, t1, t2, t1s, t2s, stadium, city, attendance in games.values_list('date', 'team1', 'team2', 'team1_score', 'team2_score', 'stadium', 'city', 'attendance'):
        total_attendance += attendance or 0
        attendance_year_dict[date.year] += attendance or 0
        if attendance is not None:
            attendance_game_count += 1

        game_year_dict[date.year] += 1

        month_dict[date.month] += 1
        team_dict[t1] += 1
        team_dict[t2] += 1
        result = tuple(sorted([t1s, t2s]))
        result_dict[result] += 1
        """



    """{
        'total_attendance': total_attendance,
        'average_attendance': total_attendance / float(attendance_game_count),
        'teams': sorted(team_dict.items(), key=lambda t: -t[1]),
        'results': sorted(result_dict.items(), key=lambda t: t[0]),
        'months': sorted(month_dict.items(), key=lambda t: t[0]),
        'game_years': sorted(game_year_dict.items(), key=lambda t: t[0]),
        'attendance_years': sorted(attendance_year_dict.items(), key=lambda t: t[0]),
        'top_attendance_games': Game.objects.order_by('-attendance')[:20],
        }"""


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    context = {
        'game': game,
        'goals': game.goal_set.order_by('minute'),
        'game_sources': GameSource.objects.filter(game=game),

        }
    return render_to_response("games/detail.html",
                              context,
                              context_instance=RequestContext(request))




def random_game_detail(request):
    import random
    games = Game.objects.count()
    game_id = random.randint(1, games)
    return game_detail(request, game_id)



