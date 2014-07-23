from django import template
from django.db.models.base import FieldError

register = template.Library()

@register.inclusion_tag('templatetags/standings.html')
def standings_table(standings, exclude=''):

    has_value = lambda i: set(e[0] for e in vals) != set([None])

    try:
        has_points = standings.exclude(points=None).exists()
        has_ties = standings.exclude(ties=None).exists()

    except AssertionError:
        # this seems incorrect
        vals = standings.values_list('points', 'ties')
        has_points, has_ties = [has_value(e) for e in range(2)]
    except FieldError:
        vals = standings.values_list('ties')
        has_ties = has_value(vals)
        has_points = False


    return {
        'standings': standings,
        'exclude': set(exclude.split(',')),
        'has_points': has_points,
        'has_ties': has_ties,
        }
