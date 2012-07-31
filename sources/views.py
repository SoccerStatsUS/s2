import datetime

from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from sources.models import Source


def source_index(request):

    sources = Source.objects.annotate(games=Count('game')).order_by('-games')
    context = {
        'sources': sources,
        }
    return render_to_response("sources/index.html",
                              context,
                              context_instance=RequestContext(request))



def source_detail(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    context = {
        'source': source,
        }
    return render_to_response("sources/detail.html",
                              context,
                              context_instance=RequestContext(request))





