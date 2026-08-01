import datetime

from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from sources.models import Source


def source_index(request):

    context = {
        'sources': Source.objects.order_by('-total', 'name')
        }
    return render(None, "sources/index.html",
                              context,
                              context_instance=RequestContext(request))



def source_detail(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    context = {
        'source': source,
        'feeds': source.feeditem_set.order_by('-dt'),
        }
    return render(None, "sources/detail.html",
                              context,
                              context_instance=RequestContext(request))





