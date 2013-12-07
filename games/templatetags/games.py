from django import template

register = template.Library()

@register.inclusion_tag('templatetags/games.html')
def games_table(games, exclude=''):

    return {
        'games': games,
        'exclude': set(exclude.split(','))
        }
