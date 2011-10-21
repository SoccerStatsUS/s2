from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.competitions.models import Season
from s2.teams.models import Team
from s2.standings.models import Standing
from s2.stats.models import Stat

def team_index(request):

    context = {
        'teams': Team.objects.all(),
        'standings': Standing.objects.filter(competition=None).order_by("-wins")
        }

    return render_to_response("teams/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    

def team_detail(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    context = {
        'team': team,
        'stats': Stat.team_stats.filter(team=team, competition=None).order_by("-minutes"),
        }

    return render_to_response("teams/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    


def team_season_detail(request, team_slug, season_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    standing = Standing.objects.get(team=team, season__slug=season_slug)
    season = standing.season

    context = {
        'team': team,
        'season': season,
        'standings': Standing.objects.filter(season=season),
        'stats': Stat.objects.filter(team=team, season=season),
        'games': team.game_set().filter(season=season),
        }

    return render_to_response("teams/season_detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    

