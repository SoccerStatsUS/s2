from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Sum
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Competition
from bios.models import Bio
from games.models import Game
from places.models import (Country, City, State, Stadium,
                          game_stats_by_country, game_stats_by_place)
from standings.models import StadiumStanding
from teams.models import Team


@cache_page(60 * 60 * 12)
def places_index(request):
        """
        Landing page for the four kinds of place.
        """
        context = {
                'country_count': Country.objects.count(),
                'state_count': State.objects.count(),
                'city_count': City.objects.count(),
                'stadium_count': Stadium.objects.count(),
                }
        return render(request, "places/index.html",
                                  context)


def country_index(request):
        """
        """


        stats = game_stats_by_country()
        countries = list(Country.objects.all())
        for country in countries:
            row = stats.get(country.id)
            country.game_count = row['games'] if row else 0
            country.total_attendance = row['attendance'] if row else None
        countries.sort(key=lambda c: (-c.game_count, c.name))

        context = {
                'countries': countries,
                }

        return render(request, "places/country_index.html",
                                  context)



@cache_page(60 * 60 * 12)
def state_index(request):
        """
        Every state, busiest first.
        """
        stats = game_stats_by_place('state')

        states = State.objects.select_related('country').annotate(
                city_count=Count('city', distinct=True),
                birth_count=Count('city__birth_set', distinct=True))

        for state in states:
                row = stats.get(state.id, {})
                state.game_count = row.get('games', 0)
                state.total_attendance = row.get('attendance')

        states = sorted(states, key=lambda s: (-s.game_count, s.name))

        context = {
                'states': states,
                'state_count': len(states),
                }
        return render(request, "places/state_index.html",
                                  context)


@cache_page(60 * 60 * 12)
def city_index(request):
        """
        Every city, busiest first.
        """
        stats = game_stats_by_place('city')

        cities = City.objects.select_related('state', 'country').annotate(
                birth_count=Count('birth_set', distinct=True))

        for city in cities:
                row = stats.get(city.id, {})
                city.game_count = row.get('games', 0)
                city.total_attendance = row.get('attendance')

        cities = sorted(cities, key=lambda c: (-c.game_count, c.name))
        page = Paginator(cities, 100).get_page(request.GET.get('page'))

        context = {
                'cities': page.object_list,
                'page': page,
                }

        return render(request, "places/city_index.html",
                                  context)



        

def stadium_index(request):

        stadiums = Stadium.objects.select_related('city').annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count', 'name')
        page = Paginator(stadiums, 100).get_page(request.GET.get('page'))

        context = {
                'stadiums': page.object_list,
                'page': page,
                }

        return render(request, "places/stadium_index.html",
                                  context)




def country_detail(request, slug):
        """
        """

        country = get_object_or_404(Country, slug=slug)

        # The United States alone is 23k games; rendering every row timed the
        # worker out. Show the most recent and say how many there are.
        all_games = country.games()
        game_count = all_games.count()
        games = all_games.order_by(F('date').desc(nulls_last=True)).select_related()[:100]

        stadiums = Stadium.objects.filter(city__country=country)
        births = Bio.objects.filter(birthplace__country=country).order_by('birthdate')
        competitions = Competition.objects.filter(scope='Country', area=country.name)
        cities = City.objects.filter(country=country)

        context = {
                'country': country,
                'games': games,
                'game_count': game_count,
                'births': births,
                'stadiums': stadiums,
                'competitions': competitions,
                'cities': cities,
                }
        return render(request, "places/country_detail.html",
                                  context)


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
        return render(request, "places/state_detail.html",
                                  context)



def city_detail(request, slug):
        """
        """

        city = City.objects.by_slug(slug)

        context = {
                'city': city,
                'teams': Team.objects.filter(city=city),
                'games': Game.objects.filter(city=city),
                'stadiums': city.stadium_set.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count')
                }

        return render(request, "places/city_detail.html",
                                  context)


def stadium_detail(request, slug):
        """
        Stadium detail view.
        """

        stadium = Stadium.objects.by_slug(slug)

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
                'recent_games': stadium.game_set.all()[:25],
                }

        return render(request, "places/stadium_detail.html",
                                  context)





def stadium_games(request, slug):
        """
        """

        stadium = Stadium.objects.by_slug(slug)

        # Compute average attendance.
        games = stadium.game_set.exclude(attendance=None)

        context = {
                'stadium': stadium,
                'games': games,
                }

        return render(request, "places/stadium_games.html",
                                  context)

        

