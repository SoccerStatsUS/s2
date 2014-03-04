from django import template

register = template.Library()

@register.inclusion_tag('templatetags/games.html')
def games_table(games, exclude=''):

    rg = games.values_list('round', 'group')
    rounds = set([e[0] for e in rg])
    groups = set([e[1] for e in rg])

    return {
        'games': games,
        'exclude': set(exclude.split(',')),
        'has_round': len(rounds - set(['', None])) > 0,
        'has_group': len(groups - set(['', None])) > 0,
        }
