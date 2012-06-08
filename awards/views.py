from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from awards.models import Award, AwardItem

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
    context = {
        'award': award,
        }
    return render_to_response('awards/detail.html',
                              context,
                              context_instance=RequestContext(request))


