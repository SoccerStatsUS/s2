from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page


from awards.models import Award, AwardItem
from bios.models import Bio

@cache_page(60 * 60 * 12)
def award_index(request):
    """
    A list of all available awards.
    """
    # Add a paginator.
    context = {
        'awards': Award.objects.all(),
        }
    return render_to_response("awards/index.html",
                              context,
                              context_instance=RequestContext(request))


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
        bio_ids = [e[0] for e in awarditems.values_list('id')]
        recipients = Bio.objects.filter(id__in=bio_ids)
    else:
        recipients = None

    context = {
        'award': award,
        'has_competition': has_competition,
        'recipients': recipients,
        'awarditems': awarditems,
        }

    
    return render_to_response('awards/detail.html',
                              context,
                              context_instance=RequestContext(request))


