from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Competition
from bios.models import Bio
from games.models import Game
from places.models import Country, City, State, Stadium


def country_index(request):
        """
        """

        context = {
                'countries': Country.objects.all(),
                }
        return render_to_response("places/country_index.html",
                                  context,
                                  context_instance=RequestContext(request))



def state_index(request):
        """
        """

        context = {
                'states': State.objects.all(),
                }
        return render_to_response("places/state_index.html",
                                  context,
                                  context_instance=RequestContext(request))



def country_detail(request, slug):
        """
        """

        country = get_object_or_404(Country, slug=slug)
        
        context = {
                'country': country,
                }
        return render_to_response("places/country_detail.html",
                                  context,
                                  context_instance=RequestContext(request))


def state_detail(request, slug):
        """
        """

        state = get_object_or_404(State, slug=slug)
        #bios = Bio.objects.filter(birthplace__state=state)
        bios = []
        
        context = {
                'state': state,
                'bios': bios,
                }
        return render_to_response("places/state_detail.html",
                                  context,
                                  context_instance=RequestContext(request))



def city_detail(request, slug):
        """
        """

        city = get_object_or_404(City, slug=slug)

        context = {
                'city': city,
                'games': Game.objects.filter(stadium__city=city),
                }

        return render_to_response("places/city_detail.html",
                                  context,
                                  context_instance=RequestContext(request))

        

def stadium_index(request):

        context = {
                'stadiums': Stadium.objects.all(),
                }

        return render_to_response("places/stadium_index.html",
                                  context,
                                  context_instance=RequestContext(request))




def stadium_detail(request, slug):
        """
        """

        stadium = get_object_or_404(Stadium, slug=slug)

        context = {
                'stadium': stadium,
                }

        return render_to_response("places/stadium_detail.html",
                                  context,
                                  context_instance=RequestContext(request))

        

