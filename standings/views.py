from django.core.paginator import Paginator
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.template import RequestContext

from standings.models import Standing


@cache_page(60 * 60 * 12)
def standings_index(request):
    """
    Every season standing on record, newest first. The all-time aggregate rows
    (season=None) live on the team standings dashboard instead.
    """
    standings = (Standing.objects.exclude(season=None)
                 .select_related('team', 'competition', 'season')
                 .order_by('-season__name', 'competition__name', '-wins'))
    page = Paginator(standings, 100).get_page(request.GET.get('page'))

    context = {
        'standings': page.object_list,
        'page': page,
        }
    return render(request, "standings/index.html",
                              context)


def bad_standings(request):
    """
    Season standings whose results don't sum to their games played.

    Done in SQL rather than a Python scan of every row, and left as a queryset
    so standings_table can introspect it.
    """
    zero = Value(0)
    played = (Coalesce('wins', zero) + Coalesce('losses', zero)
              + Coalesce('ties', zero) + Coalesce('shootout_wins', zero)
              + Coalesce('shootout_losses', zero))

    standings = (Standing.objects.exclude(season=None).exclude(games=None)
                 .annotate(result_total=played)
                 .exclude(games=F('result_total'))
                 .select_related('team', 'competition', 'season')
                 .order_by('-season__name', 'competition__name'))

    context = {
        'standings': standings,
        }

    return render(request, "standings/bad.html",
                              context)
