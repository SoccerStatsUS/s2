from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.games.models import Game


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





