from django import template
from django.db.models.base import FieldError

register = template.Library()

@register.inclusion_tag('templatetags/standings.html')
def standings_table(standings, exclude=''):

    has_value = lambda values, i: any(e[i] is not None for e in values)

    try:
        has_points = standings.exclude(points=None).exists()
        has_ties = standings.exclude(ties=None).exists()

    except (AssertionError, AttributeError, TypeError):
        # Sliced querysets can't be filtered; check the values directly.
        try:
            vals = list(standings.values_list('points', 'ties'))
        except (AttributeError, FieldError):
            vals = [(getattr(row, 'points', None), getattr(row, 'ties', None))
                    for row in standings]
        has_points, has_ties = [has_value(vals, e) for e in range(2)]
    except FieldError:
        vals = list(standings.values_list('ties'))
        has_points = False
        has_ties = has_value(vals, 0)


    return {
        'standings': standings,
        'exclude': set(exclude.split(',')),
        'has_points': has_points,
        'has_ties': has_ties,
        }
