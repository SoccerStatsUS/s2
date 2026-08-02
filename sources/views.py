import datetime

from django.db.models import Count, F, Q
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from sources.models import Source
from stats.models import Stat


def source_index(request):

    sources = Source.objects.annotate(news=Count('feeditem')).filter(
        Q(total__gt=0) | Q(news__gt=0)).order_by('-total', 'name')

    context = {
        'sources': sources,
        }
    return render(request, "sources/index.html",
                              context)



def source_detail(request, source_id):
    source = get_object_or_404(Source, id=source_id)

    stats = Stat.objects.filter(source=source)
    stats_count = stats.count()
    top_stats = stats.order_by(F('games_played').desc(nulls_last=True)).select_related()[:25]

    context = {
        'source': source,
        'feeds': source.feeditem_set.order_by('-dt'),
        'stats_count': stats_count,
        'top_stats': top_stats,
        }
    return render(request, "sources/detail.html",
                              context)





