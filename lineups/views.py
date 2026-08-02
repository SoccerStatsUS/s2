from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from lineups.models import Appearance
from lineups.forms import AppearanceForm

from collections import defaultdict


def get_appearances(GET):
    lineups = Appearance.objects.all()
    if 'team' in GET:
        t = GET['team']
        if t:
            lineups = lineups.filter(team__name__icontains=t)

    if 'player' in GET:
        e = GET['player']
        if e:
            lineups = lineups.filter(player__name__icontains=e)

    if 'on' in GET:
        e = GET['on']
        if e:
            lineups = lineups.filter(on=e)

    if 'off' in GET:
        e = GET['off']
        if e:
            lineups = lineups.filter(off=e)

    return lineups




@cache_page(60 * 60 * 12)
def lineup_index(request):
    """
    Every appearance on record, oldest first. get_appearances() still honours
    ?player= and ?team= from the query string; pagination preserves them.
    """
    appearances = (get_appearances(request.GET)
                   .select_related('player', 'team', 'game')
                   .order_by('game__date', 'game_id', 'order', 'id'))
    page = Paginator(appearances, 100).get_page(request.GET.get('page'))

    context = {
        'appearances': page.object_list,
        'page': page,
        }
    return render(request, "lineups/list.html",
                              context)


def lineup_ajax(request):    
    appearances = get_appearances(request.GET)
    context = {
        'appearances': appearances[:1000],
        }
    return render(request, "lineups/ajax.html",
                              context)

    

