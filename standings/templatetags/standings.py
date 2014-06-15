from django import template

register = template.Library()

@register.inclusion_tag('templatetags/standings.html')
def standings_table(standings, exclude=''):

    try:
        has_points = standings.exclude(points=None).exists()
        has_ties = standings.exclude(ties=None).exists()

    except AssertionError:
        # this seems incorrect
        vals = standings.values_list('points', 'ties')
        has_value = lambda i: set(e[0] for e in vals) != set([None])
        has_points, has_ties = [has_value(e) for e in range(2)]


    return {
        'standings': standings,
        'exclude': set(exclude.split(',')),
        'has_points': has_points,
        'has_ties': has_ties,
        }
