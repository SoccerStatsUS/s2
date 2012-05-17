import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game
from positions.models import Position

@cache_page(60 * 60 * 12)
def year_detail(request, year):
    # Add a paginator.
    year = int(year)
    games = Game.objects.filter(date__year=int(year))
    births = Bio.objects.filter(birthdate__year=year).order_by('birthdate')
    hires = Position.objects.filter(start__year=year)
    fires = Position.objects.filter(end__year=year)

    years = Game.objects.game_years()

    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        'years': years,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 12)
def month_detail(request, year, month):
    # Add a paginator.
    year, month = int(year), int(month)
    games = Game.objects.filter(date__year=year, date__month=month)
    births = Bio.objects.filter(birthdate__year=year, birthdate__month=month).order_by('birthdate')
    hires = Position.objects.filter(start__year=year, start__month=month)
    fires = Position.objects.filter(end__year=year, end__month=month)

    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def date_detail(request, year, month, day):
    # Add a paginator.
    d = datetime.date(int(year), int(month), int(day))
    games = Game.objects.filter(date=d)
    births = Bio.objects.filter(birthdate=d).order_by('birthdate')
    hires = Position.objects.filter(start=d)
    fires = Position.objects.filter(end=d)

    # Get other days.
    next = previous = None

    previous_game = Game.objects.filter(date__lt=d)
    if previous_game.exists():
        previous = previous_game[0].date

    next_game = Game.objects.filter(date__gt=d).order_by('date')
    if next_game.exists():
        next = next_game[0].date

    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        'date': d,
        'yesterday': previous,
        'tomorrow': next,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def day_detail(request, month, day):
    # Add a paginator.
    month, day = int(month), int(day)
    games = Game.objects.filter(date__month=month, date__day=day)
    births = Bio.objects.filter(birthdate__month=month,birthdate__day=day).order_by('birthdate')
    hires = Position.objects.filter(start__month=month, start__day=day)
    fires = Position.objects.filter(end__month=month, end__day=day)
    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 1)
def scoreboard_today(request):
    """
    Get the most recent game.
    """
    g = Game.objects.all()[0] # Most recent game
    t = g.date
    return date_detail(request, t.year, t.month, t.day)
