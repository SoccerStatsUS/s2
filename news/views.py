from django.core.paginator import Paginator
from django.shortcuts import render

from news.models import FeedItem


def news_index(request):
    """
    Every feed item on record, newest first.
    """
    items = FeedItem.objects.order_by('-dt', '-id').select_related('source')
    page = Paginator(items, 100).get_page(request.GET.get('page'))

    context = {
        'items': page.object_list,
        'page': page,
        }
    return render(request, "news/index.html", context)
