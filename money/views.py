from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from collections import defaultdict

from money.models import Salary
from bios.models import Bio


@cache_page(60 * 60 * 12)
def salaries_index(request):
    """
    Every salary on record, largest first.
    """
    salaries = (Salary.objects.select_related('person')
                .order_by('-amount', 'season', 'person__name'))
    page = Paginator(salaries, 100).get_page(request.GET.get('page'))

    seasons = sorted(set(Salary.objects.values_list('season', flat=True)))

    context = {
        'salaries': page.object_list,
        'page': page,
        'first_season': seasons[0] if seasons else None,
        'last_season': seasons[-1] if seasons else None,
        }
    return render(request, "money/index.html",
                              context)

