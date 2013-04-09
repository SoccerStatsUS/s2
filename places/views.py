from django.db.models import Avg, Count, Sum
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Competition
from bios.models import Bio
from games.models import Game
from places.models import Country, City, State, Stadium
from standings.models import StadiumStanding


def country_index(request):
        """
        """


        context = {
                'countries': Country.objects.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count'),
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


def city_index(request):

        context = {
                'cities': City.objects.all(),
                }

        return render_to_response("places/city_index.html",
                                  context,
                                  context_instance=RequestContext(request))



        

def stadium_index(request):

        context = {
                'stadiums': Stadium.objects.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count')
                }

        return render_to_response("places/stadium_index.html",
                                  context,
                                  context_instance=RequestContext(request))




def country_detail(request, slug):
        """
        """

        country = get_object_or_404(Country, slug=slug)
        stadiums = Stadium.objects.filter(city__country=country)
        births = Bio.objects.filter(birthplace__country=country).order_by('birthdate')
        competitions = Competition.objects.filter(scope='Country', area=country.name)

        context = {
                'country': country,
                'births': births,
                'stadiums': stadiums,
                'competitions': competitions,
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
                'stadiums': city.stadium_set.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count')
                }

        return render_to_response("places/city_detail.html",
                                  context,
                                  context_instance=RequestContext(request))


def stadium_detail(request, slug):
        """
        """

        stadium = get_object_or_404(Stadium, slug=slug)

        # Compute average attendance.
        games = stadium.game_set.exclude(attendance=None)
        attendance_game_count = games.count()
        average_attendance = games.aggregate(Avg('attendance'))['attendance__avg']
        standings = StadiumStanding.objects.filter(stadium=stadium).order_by('-games')

        context = {
                'stadium': stadium,
                'average_attendance': average_attendance,
                'attendance_game_count': attendance_game_count,
                'standings': standings,
                }

        return render_to_response("places/stadium_detail.html",
                                  context,
                                  context_instance=RequestContext(request))

        

