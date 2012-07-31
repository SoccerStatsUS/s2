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
        stadiums = Stadium.objects.filter(city__country=country)
        births = Bio.objects.filter(birthplace__country=country).order_by('birthdate')

        context = {
                'country': country,
                'births': births,
                'stadiums': stadiums,
                }
        return render_to_response("places/country_detail.html",
                                  context,
                                  context_instance=RequestContext(request))


def state_detail(request, slug):
        """
        """

        state = get_object_or_404(State, slug=slug)
        births = Bio.objects.filter(birthplace__state=state)
        stadiums = Stadium.objects.filter(city__state=state)
        games = Game.objects.exclude(city=None).filter(city__state=state)
        
        context = {
                'state': state,
                'births': births,
                'stadiums': stadiums,
                'games': games,
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
                'games': Game.objects.filter(city=city),
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

        

