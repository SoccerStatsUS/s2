from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.competitions.models import Competition
from s2.drafts.models import Draft

def drafts_index(request):
    context = {
        'drafts': Draft.objects.all()
        }
    return render_to_response("drafts/index.html",
                              context,
                              context_instance=RequestContext(request))



def draft_detail(request, competition_slug, draft_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    draft = get_object_or_404(Draft, competition=competition, slug=draft_slug)

    context = {
        'draft': draft,
        }
    return render_to_response("drafts/detail.html",
                              context,
                              context_instance=RequestContext(request))

