import re

from django.db.models import Count, Min, Max
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page


from awards.models import Award, AwardItem
from bios.models import Bio

@cache_page(60 * 60 * 12)
def award_index(request):
    """
    A list of all available awards.
    """
    awards = Award.objects.select_related('competition').annotate(
        item_count=Count('awarditem'),
        first_season=Min('awarditem__season__name'),
        last_season=Max('awarditem__season__name'),
        )
    awards = sorted(awards, key=lambda a: (
        a.competition is None,
        a.competition.name if a.competition else '',
        a.name,
        ))

    def year(name):
        m = re.search(r'\d{4}', name or '')
        return m.group(0) if m else None

    for award in awards:
        first, last = year(award.first_season), year(award.last_season)
        if first and last:
            award.span = first if first == last else '%s–%s' % (first, last)
        else:
            award.span = None

    context = {
        'awards': awards,
        }
    return render(request, "awards/index.html",
                              context)


@cache_page(60 * 60 * 12)
def award_detail(request, award_id):
    """
    Detail for a specific award.
    """
    award = get_object_or_404(Award, id=award_id)

    has_competition = award.competition is not None

    # Attempting to order recipients by name if theer is no competition.
    # Not possible at the moment due to use of genericforeignkey in awarditem.
    # Consider denormalizing data and cacheing.
    awarditems = award.awarditem_set.all()
    if not has_competition:
        bio_ids = [e[0] for e in awarditems.values_list('object_id')]
        recipients = Bio.objects.filter(id__in=bio_ids)
    else:
        recipients = None

    context = {
        'award': award,
        'has_competition': has_competition,
        'recipients': recipients,
        'awarditems': awarditems,
        }

    
    return render(request, 'awards/detail.html',
                              context)


