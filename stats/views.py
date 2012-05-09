from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from stats.models import Stat
from stats.forms import StatForm


def stats_index(request):
    # Should probably just redirect this to /tools/stats.

    context = {
        'stats': Stat.career_stats.all()[:100],
        'form': StatForm(),
        }
    return render_to_response("stats/list.html",
                              context,
                              context_instance=RequestContext(request))
