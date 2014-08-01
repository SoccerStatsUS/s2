
from django.db.models import Sum, Avg
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from organizations.models import Confederation


def organizations_index(request):

    context = {
        'confederations': Confederation.objects.all(),
        }
    

    return render_to_response("organizations/index.html",
                              context,
                              context_instance=RequestContext(request))



@cache_page(60 * 60 * 12)
def confederations_index(request):

    context = {
        'confederations': Confederation.objects.all(),
        }
    

    return render_to_response("organizations/confederation/index.html",
                              context,
                              context_instance=RequestContext(request))




@cache_page(60 * 60 * 12)
def confederation_detail(request, confederation_slug):
    confederation = get_object_or_404(Confederation, slug=confederation_slug)

    context = {
        'confederation': confederation,
        }

    return render_to_response("organizations/confederation/detail.html",
                              context,
                              context_instance=RequestContext(request))
