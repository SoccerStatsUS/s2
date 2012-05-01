from collections import Counter

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from goals.models import Goal
from lineups.models import Appearance



def tool_index(request):

    context = {}

    return render_to_response("tools/index.html",
                              context,
                              context_instance=RequestContext(request))




def game_search(request):

    context = {}

    return render_to_response("tools/games.html",
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

