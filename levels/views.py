
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from awards.models import Award
#from bios.models import Bio
from games.models import Game
from competitions.models import Competition, Season
#from lineups.models import Appearance
#from places.models import Country
from standings.models import Standing
from stats.models import Stat, CompetitionStat, SeasonStat




@cache_page(60 * 60 * 12)
def level_index(request):

    ctype = None


    context = {
        'competitions': competitions.select_related(),
        'form': form,
        'ctype': ctype,
        #'itype': itype,
        #'valid': form.is_valid(),
        #'errors': form.errors,

        }
    return render_to_response("levels/index.html",
                              context,
                              context_instance=RequestContext(request))




@cache_page(60 * 60 * 12)
def level_detail(request, country_slug, level):
    
    competitions = Competition.objects.filter(area='United States', code='soccer', level=int(level), ctype='League')
    seasons = Season.objects.filter(competition__in=competitions).order_by('name')
    games = Game.objects.filter(competition__in=competitions)

    standings = Standing.objects.filter(competition__in=competitions, season=None)
    
    # Change to level stat...
    stats = CompetitionStat.objects.filter(competition__in=competitions)
    if stats.exclude(games_played=None).exists():
        sx = stats.exclude(games_played=None).order_by('-games_played', '-goals')[:25]
    else:
        sx = stats.exclude(games_played=None, goals=None).order_by('-games_played', '-goals')[:25]

    awards = Award.objects.filter(competition__in=competitions)


    context = {
        'competitions': competitions,
        'seasons': seasons,
        'stats': sx,
        'games': games.select_related()[:25],
        'big_winners': standings.order_by('-wins')[:50],
        }
    return render_to_response("levels/detail.html",
                              context,
                              context_instance=RequestContext(request))

