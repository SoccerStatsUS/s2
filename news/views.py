from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from news.models import NewsSource, FeedItem

def news_index(request):
    """
    """
    # Use djangoproject.com's feed aggregator to build this.

    context = {
        'items': FeedItem.objects.order_by('-dt')[:25]
        }
    return render_to_response("news/index.html",
                              context,
                              context_instance=RequestContext(request))





def feed_detail(request, feed):
    pass
