from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.template import RequestContext

from goals.models import Goal


@cache_page(60 * 60 * 12)
def goals_index(request):
    """
    Every goal on record, oldest first.
    """
    goals = (Goal.objects
             .select_related('player', 'team', 'own_goal_player',
                             'game__team1', 'game__team2', 'game__competition')
             .order_by('date', 'minute', 'id'))
    page = Paginator(goals, 100).get_page(request.GET.get('page'))

    context = {
        'goals': page.object_list,
        'page': page,
        }
    return render(request, "goals/index.html",
                              context)


