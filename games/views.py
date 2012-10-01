import datetime

from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game
from standings.models import Standing

from collections import defaultdict


@cache_page(60 * 60 * 12)
def homepage(request):
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
    context = {
        'today': today,
        'born': Bio.objects.born_on(today.month, today.day),
        'game': Game.objects.on(today.month, today.day),
        'games': Game.objects.order_by('-date')[:10],
        'standings': Standing.objects.filter(season__competition__slug='major-league-soccer').count(), 
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


    # How to get top attendances...
    #for gid, attendance in games.values_list('date', 'team1, 'id', 'attendance'):



    context = {
        'games': games,
        'game_count': game_count,
        'total_attendance': total_attendance,
        'average_attendance': total_attendance / float(attendance_game_count),
        'teams': sorted(team_dict.items(), key=lambda t: -t[1]),
        'results': sorted(result_dict.items(), key=lambda t: t[0]),
        'months': sorted(month_dict.items(), key=lambda t: t[0]),
        'game_years': sorted(game_year_dict.items(), key=lambda t: t[0]),
        'attendance_years': sorted(attendance_year_dict.items(), key=lambda t: t[0]),
        'top_attendance_games': Game.objects.order_by('-attendance')[:20],
        

        }
    return render_to_response("games/index.html",
                              context,
                              context_instance=RequestContext(request))


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    context = {
        'game': game,
        }
    return render_to_response("games/detail.html",
                              context,
                              context_instance=RequestContext(request))







