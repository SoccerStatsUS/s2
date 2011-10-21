from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.competitions.models import Competition, Season
from s2.stats.models import Stat

def competition_index(request):
    # Add a paginator.
    competitions = Competition.objects.all()
    context = {
        'competitions': competitions,
        }
    return render_to_response("competitions/index.html",
                              context,
                              context_instance=RequestContext(request))


def competition_detail(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    context = {
        'competition': competition,
        'stats': Stat.competition_stats.filter(team=None, competition=competition).order_by("-minutes"),
        }
    return render_to_response("competitions/competition_detail.html",
                              context,
                              context_instance=RequestContext(request))




def season_detail(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    context = {
        'season': season,
        'stats': Stat.objects.filter(season=season, competition=season.competition).order_by("-minutes"),
        }
    return render_to_response("competitions/season_detail.html",
                              context,
                              context_instance=RequestContext(request))






