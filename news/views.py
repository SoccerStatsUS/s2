from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

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


def news_detail(request, item_id):
    item = get_object_or_404(FeedItem.objects.select_related('source'), id=item_id)
    return render(request, "news/detail.html", {'item': item})
