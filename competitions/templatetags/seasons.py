from django import template

register = template.Library()

@register.inclusion_tag('templatetags/seasons.html')
def seasons_table(seasons, exclude=''):

    has_attendance = set([e.total_attendance() for e in seasons]) != set([None])

    return {
        'seasons': seasons,
        'exclude': set(exclude.split(',')),
        'has_attendance': has_attendance,
        }
