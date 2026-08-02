from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from events.models import Event, Foul


@cache_page(60 * 60 * 12)
def events_index(request):
    """
    In-game events other than goals: cards, fouls, and anything else a source
    records against a minute. Nothing is loaded yet.
    """
    events = (Event.objects.select_related('game')
              .order_by('game__date', 'minute', 'id'))
    page = Paginator(events, 100).get_page(request.GET.get('page'))

    context = {
        'events': page.object_list,
        'page': page,
        'foul_count': Foul.objects.count(),
        }
    return render(request, "events/index.html",
                              context)
