from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.stats.modesl import Stat


def stats_index(request):
    stats = Stat.objects.all()
    context = {
        'stats': stats,
        }
    return render_to_response("stats/list.html",
                              context,
                              context_instance=RequestContext(request))


# Need to figure out how else to show stats.
# Probably set up a fancy team page next.
