from collections import Counter

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from games.models import Game
from goals.models import Goal
from lineups.models import Appearance
from stats.models import Stat

from tools.forms import GameSearchForm, StatSearchForm, GoalSearchForm, LineupSearchForm



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

    context = {
        'form': GoalSearchForm(),
        }

    return render_to_response("tools/goals.html",
                              context,
                              context_instance=RequestContext(request))


def lineup_search(request):

    context = {
        'form': LineupSearchForm(),
            }

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
            if t:
                games = Game.objects.filter(models.Q(team1__name__icontains=t) | models.Q(team2__name__icontains=t))

        if 'season' in request.GET:
            e = request.GET['season']
            if e:
                games = games.filter(season__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            if e:
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
        'games': games[START:END],
        }

    return render_to_response("tools/ajax/games.html",
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
            if t:
                stats = stats.filter(team__name__icontains=t)

        if 'season' in request.GET:
            e = request.GET['season']
            if e:
                stats = stats.filter(season__name__icontains=e)

        if 'name' in request.GET:
            e = request.GET['name']
            if e:
                stats = stats.filter(player__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            if e:
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

    return render_to_response("tools/ajax/stats.html",
                              context,
                              context_instance=RequestContext(request))

    


@cache_page(60 * 24)
def lineups_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_appearances(request):
        appearances = Appearance.objects.all().order_by("game")
        if 'team' in request.GET:
            t = request.GET['team']
            appearances = appearances.filter(team__name__icontains=t)

        if 'season' in request.GET:
            e = request.GET['season']
            appearances = appearances.filter(season__name__icontains=e)

        if 'name' in request.GET:
            e = request.GET['name']
            appearances = appearances.filter(player__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            appearances = appearances.filter(competition__name__icontains=e)

        if 'on_gte' in request.GET:
            e = request.GET['on_gte']
            if e:
                appearances = appearances.filter(competition__on__gte=e)
            
        if 'on_lte' in request.GET:
            e = request.GET['on_lte']
            if e:
                appearances = appearances.filter(competition__on__lte=e)

        if 'off_gte' in request.GET:
            e = request.GET['off_gte']
            if e:
                appearances = appearances.filter(competition__off__gte=e)
            
        if 'off_lte' in request.GET:
            e = request.GET['off_lte']
            if e:
                appearances = appearances.filter(competition__off__lte=e)

        if 'count' in request.GET:
            ITEMS_PER_PAGE = request.GET['count']

            if 'page' in request.GET:
                PAGE = request.GET['page']

        return appearances

    appearances = get_appearances(request)

    START = PAGE * ITEMS_PER_PAGE
    END = START + ITEMS_PER_PAGE

    context = {
        'appearances': appearances[START:END]
        }

    return render_to_response("tools/ajax/lineups.html",
                              context,
                              context_instance=RequestContext(request))

    





@cache_page(60 * 24)
def goals_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_goals(request):
        goals = Goal.objects.all().order_by("game", "-minute")
        if 'team' in request.GET:
            t = request.GET['team']
            if t:
                goals = goals.filter(team__name__icontains=t)

        if 'player' in request.GET:
            e = request.GET['player']
            if e:
                goals = goals.filter(player__name__icontains=e)

        if 'minute_lte' in request.GET:
            e = request.GET['minute_lte']
            if e:
                goals = goals.filter(minute__lte=e)

        if 'minute_gte' in request.GET:
            e = request.GET['minute_gte']
            if e:
                goals = goals.filter(minute__gte=e)


        if 'count' in request.GET:
            ITEMS_PER_PAGE = request.GET['count']

        if 'page' in request.GET:
            PAGE = request.GET['page']

        return goals

    goals = get_goals(request)

    START = PAGE * ITEMS_PER_PAGE
    END = START + ITEMS_PER_PAGE

    context = {
        'goals': goals[START:END]
        }

    return render_to_response("tools/ajax/goals.html",
                              context,
                              context_instance=RequestContext(request))

    


