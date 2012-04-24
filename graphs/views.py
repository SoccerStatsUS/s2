from collections import Counter

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from goals.models import Goal
from lineups.models import Appearance



def graphs_index(request):

    goal_minutes = [e[0] for e in Goal.objects.values_list("minute")]
    goal_dict = Counter(goal_minutes)

    lineup_minutes = [int(e[0]) for e in Appearance.objects.exclude(on=0).values_list('on')]
    lineup_dict = Counter(lineup_minutes)
    

    context = {
        'goal_tuple': sorted(goal_dict.items()),
        'lineup_tuple': sorted(lineup_dict.items()),
        }

    return render_to_response("graphs/index.html",
                              context,
                              context_instance=RequestContext(request))

