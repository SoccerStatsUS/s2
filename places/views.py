from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from s2.competitions.models import Competition
from s2.bios.models import Bio

from s2.places.models import Place, State, Country


@cache_page(60 * 60 * 12)
def place_index(request):
    places = set([e.birthplace for e in Bio.objects.exclude(birthplace=None)])
    
    context = {
        'places': sorted(places),
        }
    return render_to_response("places/index.html",
                              context,
                              context_instance=RequestContext(request))



def place_detail(request, name):

    bios = Bio.objects.filter(birthplace=name)

    context = {
        'bios': bios,
        'name': name,
        }
    return render_to_response("places/detail.html",
                              context,
                              context_instance=RequestContext(request))

