from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.competitions.models import Competition, Season


def competition_index(request):
    # Add a paginator.
    competitions = Competition.objects.all()
    context = {
        'competitions': competitions
        }
    return render_to_response("competitions/index.html",
                              context,
                              context_instance=RequestContext(request))


def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    context = {
        'competition': competition
        }
    return render_to_response("competitions/competition_detail.html",
                              context,
                              context_instance=RequestContext(request))




def season_detail(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    context = {
        'season': season
        }
    return render_to_response("competitions/season_detail.html",
                              context,
                              context_instance=RequestContext(request))






