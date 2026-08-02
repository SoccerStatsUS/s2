from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from stats.models import Stat
from stats.forms import StatForm


@cache_page(60 * 60 * 12)
def stats_index(request):
    """
    Every player-season stat line on record, newest first.
    """
    stats = (Stat.objects
             .select_related('player', 'team', 'competition', 'season')
             .order_by('-season__name', 'competition__name', '-games_played'))
    page = Paginator(stats, 100).get_page(request.GET.get('page'))

    context = {
        'stats': page.object_list,
        'page': page,
        }
    return render(request, "stats/list.html",
                              context)
