from django import template

register = template.Library()

@register.inclusion_tag('templatetags/drafts.html')
def picks_table(picks, exclude=''):

    return {
        'picks': picks,
        'exclude': set(exclude.split(',')),
        }
