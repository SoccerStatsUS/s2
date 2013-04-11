import datetime

from django.db.models import Max, Min, Count, Sum, Avg
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game
from places.models import City, Stadium
from positions.models import Position
from standings.models import Standing


@cache_page(60 * 60 * 12)
def dates_index(request):

    # All games.
    games = Game.objects.all()
    min_date = games.aggregate(Min('date'))['date__min']
    max_date = games.aggregate(Max('date'))['date__max']

    years = range(min_date.year, max_date.year + 1)

    context = {
        'years': years,
        }

    return render_to_response("dates/index.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def year_detail(request, year):
    """
    Summarize the events of the year.
    """
    year = int(year)
    games = Game.objects.filter(date__year=int(year)).order_by('date')
    births = Bio.objects.filter(birthdate__year=year).order_by('birthdate')
    deaths = Bio.objects.filter(deathdate__year=year).order_by('deathdate')
    hires = Position.objects.filter(start__year=year)
    fires = Position.objects.filter(end__year=year)

    years = Game.objects.game_years()

    stadium_ids = set([e[0] for e in games.exclude(stadium=None).values_list('stadium')])
    stadiums = Stadium.objects.filter(id__in=stadium_ids)
    
    next_date_tuple = previous_date_tuple = None

    previous_game = Game.objects.filter(date__lt=datetime.date(year, 1, 1))
    if previous_game.exists():
        previous_date = previous_game[0].date
        previous_date_tuple = (previous_date.year, '', '')

    next_game = Game.objects.filter(date__gt=datetime.date(year, 12, 31)).order_by('date')
    if next_game.exists():
        next_date = next_game[0].date
        next_date_tuple = (next_date.year, '', '')

    context = {
        'games': games.select_related(),
        'births': births.select_related(),
        'hires': hires.select_related(),
        'fires': fires.select_related(),
        'years': years,
        'stadiums': stadiums,
        'date': str(year),
        'previous_date': previous_date_tuple,
        'next_date': next_date_tuple,

        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 12)
def month_detail(request, year, month):
    """
    Summarize the events of the month.
    """

    if month == '':
        return year_detail(request, year)

    year, month = int(year), int(month)
    games = Game.objects.filter(date__year=year, date__month=month).order_by('date')
    births = Bio.objects.filter(birthdate__year=year, birthdate__month=month).order_by('birthdate')
    deaths = Bio.objects.filter(deathdate__year=year, deathdate__month=month).order_by('deathdate')
    hires = Position.objects.filter(start__year=year, start__month=month)
    fires = Position.objects.filter(end__year=year, end__month=month)

    stadium_ids = set([e[0] for e in games.exclude(stadium=None).values_list('stadium')])
    stadiums = Stadium.objects.filter(id__in=stadium_ids)

    next_date_tuple = previous_date_tuple = None

    previous_game = Game.objects.filter(date__lt=datetime.date(year, month, 1))
    if previous_game.exists():
        previous_date = previous_game[0].date
        previous_date_tuple = (previous_date.year, previous_date.month, '')


    if month == 12:
        next_game = Game.objects.filter(date__gte=datetime.date(year+1, 1, 1)).order_by('date')
    else:
        next_game = Game.objects.filter(date__gte=datetime.date(year, month + 1, 1)).order_by('date')

    if next_game.exists():
        next_date = next_game[0].date
        next_date_tuple = (next_date.year, next_date.month, '')



    context = {
        'games': games.select_related(),
        'births': births,
        'hires': hires,
        'fires': fires,
        'stadiums': stadiums[:20],
        'date': '%s/%s' % (month, year),
        'previous_date': previous_date_tuple,
        'next_date': next_date_tuple,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def date_detail(request, year, month, day):
    """
    Summarize the events of the day.
    """


    if day == '':
        return month_detail(request, year, month)

    d = datetime.date(int(year), int(month), int(day))
    games = Game.objects.filter(date=d).order_by('date')
    births = Bio.objects.filter(birthdate=d).order_by('birthdate')
    deaths = Bio.objects.filter(deathdate=d).order_by('deathdate')
    hires = Position.objects.filter(start=d)
    fires = Position.objects.filter(end=d)

    stadium_ids = set([e[0] for e in games.exclude(stadium=None).values_list('stadium')])
    stadiums = Stadium.objects.filter(id__in=stadium_ids)

    standings = Standing.objects.filter(date=d)


    next_date_tuple = previous_date_tuple = None

    previous_game = Game.objects.filter(date__lt=d)
    if previous_game.exists():
        previous_date = previous_game[0].date
        previous_date_tuple = (previous_date.year, previous_date.month, previous_date.day)

    next_game = Game.objects.filter(date__gt=d).order_by('date')
    if next_game.exists():
        next_date = next_game[0].date
        next_date_tuple = (next_date.year, next_date.month, next_date.day)

    context = {
        'games': games.select_related(),
        'births': births,
        'hires': hires,
        'fires': fires,
        'date': '%s/%s/%s' % (d.month, d.day, d.year),
        'previous_date': previous_date_tuple,
        'next_date': next_date_tuple,
        'stadiums': stadiums[:20],
        'standings': standings,
        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def day_detail(request, month, day):
    """
    This day in history.
    """
    month, day = int(month), int(day)

    d = datetime.date(2012, month, day)
    next_day = d + datetime.timedelta(days=1)
    previous_day = d - datetime.timedelta(days=1)
    day_string = "%s/%s" % (month, day)

    games = Game.objects.filter(date__month=month, date__day=day)
    births = Bio.objects.filter(birthdate__month=month,birthdate__day=day).order_by('birthdate')
    deaths = Bio.objects.filter(deathdate__month=month, deathdate__day=day).order_by('deathdate')
    hires = Position.objects.filter(start__month=month, start__day=day)
    fires = Position.objects.filter(end__month=month, end__day=day)
    context = {
        'games': games.select_related(),
        'births': births,
        'hires': hires,
        'fires': fires,

        'day_string': day_string,
        'next_day': next_day,
        'previous_day': previous_day,

        }
    return render_to_response("dates/list.html",
                              context,
                              context_instance=RequestContext(request))

@cache_page(60 * 60 * 1)
def scoreboard_today(request):
    """
    The scoreboard for the most recent day with games.
    """
    today = datetime.date.today()
    g = Game.objects.exclude(date=None).exclude(date__gt=today)[0] # Most recent game
    t = g.date
    return date_detail(request, t.year, t.month, t.day)
