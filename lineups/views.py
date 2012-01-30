from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from lineups.models import Appearance
from lineups.forms import AppearanceForm


def get_appearances(request):
    lineups = Appearance.objects.all()
    if 'team' in request.GET:
        t = request.GET['team']
        if t:
            lineups = lineups.filter(team__name__icontains=t)

    if 'player' in request.GET:
        e = request.GET['player']
        if e:
            lineups = lineups.filter(player__name__icontains=e)

    if 'on' in request.GET:
        e = request.GET['on']
        if e:
            lineups = lineups.filter(on=e)

    if 'off' in request.GET:
        e = request.GET['off']
        if e:
            lineups = lineups.filter(off=e)

    return lineups




def lineup_index(request):
    appearances = get_appearances(request)
    context = {
        'appearances': appearances[:1000],
        'form': AppearanceForm(),
        }
    return render_to_response("lineups/list.html",
                              context,
                              context_instance=RequestContext(request))


def lineup_ajax(request):    
    appearances = get_appearances(request)
    context = {
        'appearances': appearances[:1000],
        }
    return render_to_response("lineups/ajax.html",
                              context,
                              context_instance=RequestContext(request))

    

