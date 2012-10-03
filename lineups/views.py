from django.shortcuts import render_to_response, get_object_or_404
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




def lineup_index(request):
    # No reason to set this up a a form.
    # Just show interesting stuff.
    appearances = get_appearances(request.GET)

    for appearance in appearances.values_list(''):
        pass


    context = {
        'appearances': appearances[:1000],
        'form': AppearanceForm(),
        }
    return render_to_response("lineups/list.html",
                              context,
                              context_instance=RequestContext(request))


def lineup_ajax(request):    
    appearances = get_appearances(request.GET)
    context = {
        'appearances': appearances[:1000],
        }
    return render_to_response("lineups/ajax.html",
                              context,
                              context_instance=RequestContext(request))

    

