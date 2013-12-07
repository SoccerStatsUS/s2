from django import template

register = template.Library()

@register.inclusion_tag('datum_or_grey.html')
def datum_or_grey(datum):
    return {
        'datum': datum,
        'is_none': datum is None,
        'is_zero': datum == 0,
        }
