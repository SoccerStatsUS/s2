from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from news.models import NewsSource

def news_index(request):
    context = {
        'news_sources': NewsSource.objects.all()
        }
    return render_to_response("news/index.html",
                              context,
                              context_instance=RequestContext(request))

