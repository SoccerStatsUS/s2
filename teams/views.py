from collections import defaultdict, OrderedDict

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from competitions.models import Season
from teams.models import Team
from standings.models import Standing
from stats.models import Stat

from django.views.decorators.cache import cache_page

def team_list_generic(request, team_list=None):

    if team_list is None:
        standings = Standing.objects.filter(competition=None).order_by("-wins")[:1000]
    else:
        standings = Standing.objects.filter(competition=None, team__in=team_list)

    context =  {
        'standings': standings,
        }
    return render_to_response("teams/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )    


def team_index(request):
    standings = Standing.objects.filter(competition=None).order_by("-wins")
    return team_list_generic(request, standings)

def team_name_fragment(request, fragment):
    return team_list_generic(request,
                               Team.objects.filter(name__istartswith=fragment))



@cache_page(60 * 60 * 12)
def team_index_new(request):
    
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    name_dict = OrderedDict()

    for letter in letters:
        standings = Standing.objects.filter(competition=None, team__name__istartswith=letter).order_by('-wins')[:5]
        stats = Stat.career_stats.filter(player__name__istartswith=letter)[:5]
        name_dict[letter] = stats

    context = {
        'name_dict': name_dict
        }

    return render_to_response("teams/index.html",
                              context,
                              context_instance=RequestContext(request))



def seasons_dashboard(request):
    season_names = defaultdict(list)
    for season in Season.objects.all():
        season_names[season.name].append(season)

    context = {
        'season_dict': season_names,
        'seasons': sorted(season_names.keys()),
        }

    return render_to_response("teams/seasons.html",
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
        'stats': Stat.team_stats.filter(team=team, competition=None),
        }

    return render_to_response("teams/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    


def team_year_detail(request, team_slug, year):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    seasons = Season.objects.filter(name=year)

    chart_years, chart = team.player_chart(year)

    context = {
        'team': team,
        'standings': Standing.objects.filter(team=team, season__in=seasons),
        'stats': Stat.objects.filter(team=team, season__in=seasons),
        'games': team.game_set().filter(date__year=year),
        'chart': chart,
        'chart_years': chart_years,
        }

    return render_to_response("teams/year_detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    


@cache_page(60 * 24)
def teams_ajax(request):
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

    


def bad_teams(request):


    
    context = {
        'duplicate_slugs': Team.objects.duplicate_slugs(),
        }

    return render_to_response("teams/bad.html",
                              context,
                              context_instance=RequestContext(request)
                              )    
                              
