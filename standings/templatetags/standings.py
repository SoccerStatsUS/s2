from django import template

register = template.Library()

@register.inclusion_tag('templatetags/standings.html')
def standings_table(standings, exclude=''):

    return {
        'standings': standings,
        'exclude': set(exclude.split(','))
        }
