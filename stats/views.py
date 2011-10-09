from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.stats.models import Stat


def stats_index(request):
    context = {
        'stats': Stat.career_stats.all(),
        }
    return render_to_response("stats/list.html",
                              context,
                              context_instance=RequestContext(request))

