from collections import Counter

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from goals.models import Goal
from lineups.models import Appearance

from tools.forms import GameSearchForm, StatSearchForm



def tool_index(request):
    
    context = {}

    return render_to_response("tools/index.html",
                              context,
                              context_instance=RequestContext(request))




def game_search(request):

    context = {
        'form': GameSearchForm(),
        }

    return render_to_response("tools/games.html",
                              context,
                              context_instance=RequestContext(request))

def stat_search(request):

    context = {
        'form': StatSearchForm(),
        }

    return render_to_response("tools/stats.html",
                              context,
                              context_instance=RequestContext(request))




def goal_search(request):

    context = {}

    return render_to_response("tools/goals.html",
                              context,
                              context_instance=RequestContext(request))


def lineup_search(request):

    context = {}

    return render_to_response("tools/lineups.html",
                              context,
                              context_instance=RequestContext(request))






@cache_page(60 * 24)
def games_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_games(request):
        games = Game.objects.all().order_by("-date")

        if 'team' in request.GET:
            t = request.GET['team']
            games = Game.objects.filter(models.Q(team1__name__icontains=t) | models.Q(team2__name__icontains=t))

        if 'season' in request.GET:
            e = request.GET['season']
            games = games.filter(season__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            games = games.filter(competition__name__icontains=e)

        if 'count' in request.GET:
            ITEMS_PER_PAGE = request.GET['count']

        if 'page' in request.GET:
            PAGE = request.GET['page']

        return games

    games = get_games(request)

    START = PAGE * ITEMS_PER_PAGE
    END = START + ITEMS_PER_PAGE

    context = {
        'gamesx': games[START:END],
        'games': Game.objects.all()[:100]
        }

    return render_to_response("games/ajax.html",
                              context,
                              context_instance=RequestContext(request))

    





@cache_page(60 * 24)
def stats_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_stats(request):
        stats = Stat.objects.all().order_by("-minutes")
        if 'team' in request.GET:
            t = request.GET['team']
            stats = stats.filter(team__name__icontains=t)

        if 'season' in request.GET:
            e = request.GET['season']
            stats = stats.filter(season__name__icontains=e)

        if 'name' in request.GET:
            e = request.GET['name']
            stats = stats.filter(player__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            stats = stats.filter(competition__name__icontains=e)

        if 'count' in request.GET:
            ITEMS_PER_PAGE = request.GET['count']

            if 'page' in request.GET:
                PAGE = request.GET['page']

        return stats

    stats = get_stats(request)

    START = PAGE * ITEMS_PER_PAGE
    END = START + ITEMS_PER_PAGE

    context = {
        'stats': stats[START:END]
        }

    return render_to_response("stats/ajax.html",
                              context,
                              context_instance=RequestContext(request))

    


