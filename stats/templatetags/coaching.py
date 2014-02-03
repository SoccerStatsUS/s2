from django import template

register = template.Library()

@register.inclusion_tag('templatetags/coaching.html')
def coaching(coach_stats, exclude=''):


    return {
        'coach_stats': coach_stats,
        }
