from django.db.models import Sum
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Competition, Season
from stats.models import Stat

#@cache_page(60 * 60 * 12)
def competition_index(request):
    # Add a paginator.
    competitions = Competition.objects.all()
    context = {
        'competitions': competitions,
        }
    return render_to_response("competitions/index.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 12)
def competition_detail(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    context = {
        'competition': competition,
        'stats': Stat.competition_stats.filter(team=None, competition=competition).order_by('-games_played')[:25],
        'games': competition.game_set.all()[:25],
        }
    return render_to_response("competitions/competition_detail.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 12)
def competition_stats(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    context = {
        'competition': competition,
        'stats': Stat.competition_stats.filter(team=None, competition=competition).order_by('-games_played'),
        }
    return render_to_response("competitions/competition_stats.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def competition_games(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    context = {
        'competition': competition,
        'games': competition.game_set.all(),

        }
    return render_to_response("competitions/competition_games.html",
                              context,
                              context_instance=RequestContext(request))



@cache_page(60 * 60 * 12)
def season_detail(request, competition_slug, season_slug):
    """
    Detail for a given season, e.g. Major League Soccer, 1996.
    """
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season, competition=season.competition)

    # Aggregate returns None given a None value.
    mstats = stats.exclude(minutes=None)
    total_minutes = mstats.aggregate(Sum('minutes'))['minutes__sum']
    known_minutes = mstats.exclude(player__birthdate=None).aggregate(Sum('minutes'))['minutes__sum']

    goal_leaders = stats.order_by('-goals')
    game_leaders = stats.order_by('-games_played')

    context = {
        'season': season,
        'stats': stats.exists(),
        'total_minutes': total_minutes,
        'known_minutes': known_minutes,
        'goal_leaders': goal_leaders[:10],
        'game_leaders': game_leaders[:10],
        }
    return render_to_response("competitions/season_detail.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def season_stats(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    #'stats': Stat.objects.filter(team=None, season=season).order_by('-games_played'),

    context = {
        'season': season,
        'stats': Stat.objects.filter(season=season).order_by('-games_played'),
        }
    return render_to_response("competitions/season_stats.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def season_games(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    context = {
        'season': season,
        'games': competition.game_set.filter(season=season)

        }
    return render_to_response("competitions/season_games.html",
                              context,
                              context_instance=RequestContext(request))




def season_names(request):
    """
    Show the set of all distinct season names.
    """
    
    names = [e[0] for e in Season.objects.values_list('name')]
    names = sorted(set(names))

    context = {
        'names': names,
        }
    
    return render_to_response("competitions/season_names.html",
                              context,
                              context_instance=RequestContext(request))

    

def season_list(request, season_slug):
    """
    List all seasons of with a given slug.
    """

    seasons = Season.objects.filter(slug=season_slug)

    context = {
        'season_exists': seasons.exists(),
        'seasons': seasons,
        }

    return render_to_response("competitions/season_list.html",
                              context,
                              context_instance=RequestContext(request))




