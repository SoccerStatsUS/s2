from django import template

register = template.Library()

@register.inclusion_tag('templatetags/stats.html')
def stats_table(stats, exclude=''):

    return {
        'stats': stats,
        'exclude': set(exclude.split(','))
        }
