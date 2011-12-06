from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from s2.stats.models import Stat
from s2.stats.forms import StatForm


def stats_index(request):
    context = {
        'stats': Stat.career_stats.all()[:100],
        'form': StatForm(),
        }
    return render_to_response("stats/list.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 24)
def stats_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_stats(request):
        stats = Stat.objects.all().order_by("-minutes")
        if 'team' in request.GET:
            t = request.GET['team']
            stats = stats.filter(team__name__icontains=t)

        if 'season' in request.GET:
            e = request.GET['season']
            stats = stats.filter(season__name__icontains=e)

        if 'name' in request.GET:
            e = request.GET['name']
            stats = stats.filter(player__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            stats = stats.filter(competition__name__icontains=e)

        return stats

    stats = get_stats(request)

    context = {
        'stats': stats[:1000],
        }

    return render_to_response("stats/ajax.html",
                              context,
                              context_instance=RequestContext(request))

    

