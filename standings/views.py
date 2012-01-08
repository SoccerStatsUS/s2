from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.standings.models import Standing


def none_sum(*args):
    s = 0
    for e in args:
        if e:
            s += e
    return s

def bad_standings(request):
    bad_standings = [e for e in Standing.objects.exclude(season=None) if e.games != e.wins + none_sum(e.losses, e.ties, e.shootout_wins, e.shootout_losses)]

    context = {
        'standings': bad_standings,
        }

    return render_to_response("standings/index.html",
                              context,
                              context_instance=RequestContext(request))

                     
