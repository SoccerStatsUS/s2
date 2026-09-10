from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from competitions.models import Competition
from stats.models import Stat
from teams.models import Team


@cache_page(60 * 60 * 12)
def stats_index(request):
    """
    Every player-season stat line on record, newest first; narrowed by
    ?competition=<slug>, ?season=<name> and ?team=<slug>, in any combination.
    """
    picked = {k: request.GET.get(k, '') for k in ('competition', 'season', 'team')}
    stats = Stat.objects.all()
    if picked['competition']:
        stats = stats.filter(competition__slug=picked['competition'])
    if picked['season']:
        stats = stats.filter(season__name=picked['season'])
    if picked['team']:
        stats = stats.filter(team__slug=picked['team'])

    # Each list offers only what exists under the other two choices.
    def under(*others):
        qs = Stat.objects.all()
        if 'competition' in others and picked['competition']:
            qs = qs.filter(competition__slug=picked['competition'])
        if 'season' in others and picked['season']:
            qs = qs.filter(season__name=picked['season'])
        if 'team' in others and picked['team']:
            qs = qs.filter(team__slug=picked['team'])
        return qs

    competitions = (Competition.objects
                    .filter(id__in=under('season', 'team').values('competition'))
                    .order_by('name'))
    seasons = (under('competition', 'team')
               .order_by('-season__name').values_list('season__name', flat=True).distinct())
    teams = (Team.objects
             .filter(id__in=under('competition', 'season').values('team'))
             .order_by('name'))

    rows = (stats
            .select_related('player', 'team', 'competition', 'season')
            .order_by('-season__name', 'competition__name', '-games_played'))
    page = Paginator(rows, 100).get_page(request.GET.get('page'))

    totals = stats.aggregate(players=Count('player', distinct=True), teams=Count('team', distinct=True),
                             goals=Sum('goals'), minutes=Sum('minutes'))

    # A column a season for the current filter, each linking to that season's lines.
    others = {k: v for k, v in picked.items() if v and k != 'season'}
    by_season = [
        {'name': row['season__name'], 'count': row['n'],
         'url': '?' + urlencode({**others, 'season': row['season__name']})}
        for row in stats.values('season__name').annotate(n=Count('id')).order_by('season__name')]

    context = {
        'stats': page.object_list,
        'page': page,
        'picked': picked,
        'filtered': any(picked.values()),
        'totals': totals,
        'by_season': by_season,
        'competitions': competitions,
        'seasons': seasons,
        'teams': teams,
        }
    return render(request, "stats/list.html", context)
