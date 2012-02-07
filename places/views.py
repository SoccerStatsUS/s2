from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Competition
from bios.models import Bio
from places.models import Country, City, Stadium


def country_index(request):
        context = {
                'countries': Country.objects.all(),
                }
        return render_to_response("places/country_index.html",
                                  context,
                                  context_instance=RequestContext(request))




def country_detail(request, slug):
        country = get_object_or_404(Country, slug=slug)
        
        context = {
                'country': country,
                }
        return render_to_response("places/country_detail.html",
                                  context,
                                  context_instance=RequestContext(request))

