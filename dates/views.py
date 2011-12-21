import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from s2.bios.models import Bio
from s2.games.models import Game
from s2.positions.models import Position

def year_detail(request, year):
    # Add a paginator.
    year = int(year)
    games = Game.objects.filter(date__year=int(year))
    births = Bio.objects.filter(birthdate__year=year).order_by('birthdate')
    hires = Position.objects.filter(start__year=year)
    fires = Position.objects.filter(end__year=year)

    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        }
    return render_to_response("games/list.html",
                              context,
                              context_instance=RequestContext(request))


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
    return render_to_response("games/list.html",
                              context,
                              context_instance=RequestContext(request))



def date_detail(request, year, month, day):
    # Add a paginator.
    d = datetime.date(int(year), int(month), int(day))
    games = Game.objects.filter(date=d)
    births = Bio.objects.filter(birthdate=d).order_by('birthdate')
    hires = Position.objects.filter(start=d)
    fires = Position.objects.filter(end=d)
    context = {
        'games': games,
        'births': births,
        'hires': hires,
        'fires': fires,
        }
    return render_to_response("games/list.html",
                              context,
                              context_instance=RequestContext(request))


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
    return render_to_response("games/list.html",
                              context,
                              context_instance=RequestContext(request))
