from django import template
from django.db.models import Prefetch

from games.spine import build_spine
from goals.models import Goal

register = template.Library()

@register.inclusion_tag('templatetags/games.html')
def games_table(games, exclude='', source_urls=False):
    """
    source_urls turns the trailing source count into a link to the page each
    game was taken from; the games must carry a source_url annotation.
    """

    rg = games.values_list('round', 'group')
    rounds = set([e[0] for e in rg])
    groups = set([e[1] for e in rg])

    # A row touches both teams, the competition, season, referee and venue,
    # plus a source count and a goal tooltip. Fetched per game, a 4,000-game
    # year page was tens of thousands of queries. This select_related
    # replaces any the caller set, so it has to name everything the row uses.
    games = games.select_related(
        'team1', 'team2', 'competition', 'season', 'referee',
        'stadium', 'city__state', 'city__country', 'country',
    ).prefetch_related(
        'sources',
        Prefetch('goal_set', to_attr='prefetched_goals',
                 queryset=Goal.objects.select_related('team', 'player').order_by('minute', 'team')),
    )

    return {
        'games': games,
        'exclude': set(exclude.split(',')),
        'has_round': len(rounds - set(['', None])) > 0,
        'has_group': len(groups - set(['', None])) > 0,
        'source_urls': source_urls,
        }


@register.inclusion_tag('templatetags/games/detail/spine.html')
def event_spine(game):
    goals = game.goal_set.select_related('player', 'own_goal_player')
    lineups = game.gamestat_set.all()
    if not lineups.exists():
        lineups = game.appearance_set.all()
    return {
        'game': game,
        'spine': build_spine(game, goals, lineups.select_related('player')),
    }
