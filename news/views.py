from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from news.models import FeedItem
from sources.models import Source


def news_index(request):
    """
    Every feed item on record, newest first; one source at a time with ?source=.
    """
    sources = list(Source.objects.annotate(n=Count('feeditem')).filter(n__gt=0).order_by('-n', 'name'))
    by_slug = {s.slug: s for s in sources}
    source = by_slug.get(request.GET.get('source', ''))

    items = FeedItem.objects.order_by('-dt', '-id').select_related('source')
    if source:
        items = items.filter(source=source)
    page = Paginator(items, 100).get_page(request.GET.get('page'))

    context = {
        'items': page.object_list,
        'page': page,
        'sources': sources,
        'source': source,
        }
    return render(request, "news/index.html", context)


def news_detail(request, archive_id):
    item = get_object_or_404(FeedItem.objects.select_related('source'), archive_id=archive_id)
    context = {
        'item': item,
        'people': item.people.order_by('name'),
        }
    return render(request, "news/detail.html", context)
