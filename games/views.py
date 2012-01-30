import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game


@cache_page(60 * 60 * 12)
def homepage(request):
    """
    The site homepage.
    """
    today = datetime.date.today()
    context = {
        'today': today,
        'born': Bio.objects.born_on(today.month, today.day),
        'game': Game.objects.on(today.month, today.day),
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





