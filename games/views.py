import datetime

from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game
from standings.models import Standing


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
    
    games = Game.objects.order_by("-date")[:50]
    context = {
        'games': games,
        }
    return render_to_response("games/list.html",
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







