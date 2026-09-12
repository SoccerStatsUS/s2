import datetime

from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, F
from django.http import Http404
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.cache import cache_page

from bios.models import Bio
from competitions.models import Competition
from games.models import Game, GameSource
from sources.models import Source
from goals.models import Goal
from standings.models import Standing
from stats.models import Stat, CareerStat
from teams.models import Team

from collections import defaultdict


def everything(request):
    return render(request, "everything.html",
                  {'today': datetime.date.today()})


@cache_page(60 * 60)
def about(request):

    first_game = Game.objects.exclude(date=None).select_related(
        'team1', 'team2', 'competition').order_by('date').first()

    context = {
        'first_game': first_game,
        'games': Game.objects.count(),
        'players': Bio.objects.count(),
        'teams': Team.objects.count(),
        'competitions': Competition.objects.count(),
        }

    return render(request, "about/index.html", context)


def coverage_by_decade():
    """
    The shape of the record itself: how many games are on file per decade, and
    how much is known about them.

    A sketch, and deliberately coarse. Four questions per decade -- is there a
    date, a lineup, a named scorer, a crowd figure -- because those are the
    four things a reader asks of an old game and the four the database answers
    separately. The share is of the decade's own games, so a thin decade and a
    fat one can be compared on how well each is known rather than on how big
    it is.

    Decades with no games at all are still returned. A gap in the middle of the
    record is a fact about the record.
    """
    from django.db.models.functions import ExtractYear
    from lineups.models import Appearance

    dated = Game.objects.exclude(date=None)
    first = dated.order_by('date').values_list('date', flat=True).first()
    last = dated.order_by('-date').values_list('date', flat=True).first()
    if first is None:
        return []

    def by_decade(queryset):
        rows = (queryset.annotate(year=ExtractYear('date')).values('year')
                .annotate(n=models.Count('id', distinct=True)))
        totals = defaultdict(int)
        for row in rows:
            if row['year']:
                totals[row['year'] // 10 * 10] += row['n']
        return totals

    games = by_decade(dated)
    attended = by_decade(dated.exclude(attendance=None))
    scored = by_decade(dated.filter(goal__isnull=False))
    lineups = by_decade(dated.filter(
        id__in=Appearance.objects.values('game_id')))

    rows = []
    for decade in range(first.year // 10 * 10, last.year // 10 * 10 + 10, 10):
        total = games.get(decade, 0)
        share = (lambda n: 100.0 * n / total if total else None)
        rows.append({
            'name': "%ds" % decade,
            'count': total,
            'lineups': lineups.get(decade, 0),
            'lineup_share': share(lineups.get(decade, 0)),
            'scored': scored.get(decade, 0),
            'scored_share': share(scored.get(decade, 0)),
            'attended': attended.get(decade, 0),
            'attended_share': share(attended.get(decade, 0)),
            })
    return rows


@cache_page(60 * 60 * 12)
def coverage(request):
    """
    The one coverage note.

    Every page that shows a summed total links here rather than restating in
    prose what it does and doesn't include. The numbers are counted live so the
    page can't drift from the database the way a hand-written paragraph would.
    """
    from events.models import Event
    from lineups.models import Appearance

    games = Game.objects.count()
    goals = Goal.objects.count()
    stat_lines = Stat.objects.count()

    context = {
        'games': games,
        'games_dated': Game.objects.exclude(date=None).count(),
        'games_with_attendance': Game.objects.exclude(attendance=None).count(),
        'goals': goals,
        'goals_with_minute': Goal.objects.exclude(minute=None).count(),
        'appearances': Appearance.objects.count(),
        'appearances_with_minutes': Appearance.objects.exclude(minutes=None).count(),
        'stat_lines': stat_lines,
        'stat_lines_with_minutes': Stat.objects.exclude(minutes=None).count(),
        'events': Event.objects.count(),
        'bios': Bio.objects.count(),
        'bios_with_birthdate': Bio.objects.exclude(birthdate=None).count(),
        'decades': coverage_by_decade(),
        }

    return render(request, "about/coverage.html", context)


@cache_page(60 * 30)
def homepage(request):

    today = datetime.date.today()
    month, day = today.month, today.day

    todays_games = Game.objects.filter(date__month=month, date__day=day).select_related()
    oldest = todays_games.order_by('date').first()
    crowd = todays_games.exclude(attendance=None).order_by('-attendance').first()
    if crowd is not None and oldest is not None and crowd.pk == oldest.pk:
        crowd = None

    born = Bio.objects.born_on(month, day)

    context = {
        'today': today,
        'oldest': oldest,
        'crowd': crowd,
        'born': born,
        'game_years': game_years(),
        'games': Game.objects.count(),
        'players': Bio.objects.count(),
        'teams': Team.objects.count(),
        'competitions': Competition.objects.count(),
        }

    return render(request, "homepage.html",
                              context)


def game_years():
    """
    A row per year from the first recorded game to the last, for the homepage
    chart. Years inside the range with nothing on record keep their slot and
    count zero -- the empty columns are the point, since they are where the
    record thins out rather than where the soccer stopped.
    """
    counts = {row['date__year']: row['n'] for row in
              Game.objects.exclude(date=None).values('date__year').annotate(n=Count('id'))}
    if not counts:
        return []

    return [{'name': str(year),
             'count': counts.get(year, 0),
             'url': reverse('year_detail', args=[year]) if counts.get(year) else None}
            for year in range(min(counts), max(counts) + 1)]


def search(request):

    q = request.GET.get('q', '').strip()

    players = teams = competitions = []
    if q:
        players = Bio.objects.filter(name__unaccent__icontains=q).order_by('name')[:30]
        teams = Team.objects.filter(name__unaccent__icontains=q).order_by('name')[:30]
        competitions = Competition.objects.filter(name__unaccent__icontains=q).order_by('name')[:30]

    context = {
        'query': q,
        'players': players,
        'teams': teams,
        'competitions': competitions,
        }

    return render(request, "search/search.html",
                              context)



@cache_page(60 * 60 * 12)
def homepage_old(request):
    """
    The site homepage. Currently badly underperfoming.
    """

    # Homepage fixes.
    # Shrink the size of the On This Day Box, move lower.
    # Add Standings.
    # Add tab for games from different competitions.
    # Add News
    # Add detailed links to different parts of the website.

    # What are the cool things you can get on the site?
    # Player +/-
    # Manager details
    # Career stats
    # Stats across competitions
    # Breadcrumbs?

    today = datetime.date.today()

    game_leaders = CareerStat.objects.exclude(games_played=None).order_by('-games_played')[:10]
    goal_leaders = CareerStat.objects.exclude(goals=None).order_by('-goals')[:10]

    recent_games = Game.objects.exclude(date=None).filter(date__lt=today).exclude(team1_result='').order_by('-date')[:10]

    goals = Goal.objects.count()


    try:
        mls_game = Game.objects.filter(competition__slug='major-league-soccer').order_by('date')[0]
    except:
        mls_game = None

    try:
        oc_game = Game.objects.get(competition__slug='us-open-cup', season__name='1924', round='f')
    except:
        oc_game = None

    context = {
        'today': today,
        'born': Bio.objects.born_on(today.month, today.day),
        'games': recent_games,
        'standings': Standing.objects.filter(season__competition__slug='major-league-soccer').count(), 
        'game_leaders': game_leaders,
        'goal_leaders': goal_leaders,
        'game_count': Game.objects.count(),
        'bio_count': Bio.objects.count(),
        'team_count': Team.objects.count(),
        'competition_count': Competition.objects.count(),

        'mls_game': mls_game,
        'oc_game': oc_game,
        
        }
    return render(request, "homepage.html",
                              context)

def games_qa(request):
    
    context = {
        'duplicate_games': Game.objects.duplicate_games(),
        }

    return render(request, "games/qa.html",
                              context)    

    

@cache_page(60 * 60 * 12)
def games_index(request):
    """
    Every game on record, oldest first. Undated games sort last rather than
    leading the list, so page 1 opens on 1866 instead of on the unknowns.
    """
    games = Game.objects.order_by(
        F('date').asc(nulls_last=True), 'id').select_related().prefetch_related('sources')
    page = Paginator(games, 100).get_page(request.GET.get('page'))

    context = {
        'games': page.object_list,
        'page': page,
        }

    return render(request, "games/index.html",
                              context)

    """
    attendance_game_count = 0
    total_attendance = 0

    month_dict = defaultdict(int)
    team_dict = defaultdict(int)
    result_dict = defaultdict(int)

    game_year_dict = defaultdict(int)
    attendance_year_dict = defaultdict(int)

    # Pull this out.
    for date, t1, t2, t1s, t2s, stadium, city, attendance in games.values_list('date', 'team1', 'team2', 'team1_score', 'team2_score', 'stadium', 'city', 'attendance'):
        total_attendance += attendance or 0
        attendance_year_dict[date.year] += attendance or 0
        if attendance is not None:
            attendance_game_count += 1

        game_year_dict[date.year] += 1

        month_dict[date.month] += 1
        team_dict[t1] += 1
        team_dict[t2] += 1
        result = tuple(sorted([t1s, t2s]))
        result_dict[result] += 1
        """



    """{
        'total_attendance': total_attendance,
        'average_attendance': total_attendance / float(attendance_game_count),
        'teams': sorted(team_dict.items(), key=lambda t: -t[1]),
        'results': sorted(result_dict.items(), key=lambda t: t[0]),
        'months': sorted(month_dict.items(), key=lambda t: t[0]),
        'game_years': sorted(game_year_dict.items(), key=lambda t: t[0]),
        'attendance_years': sorted(attendance_year_dict.items(), key=lambda t: t[0]),
        'top_attendance_games': Game.objects.order_by('-attendance')[:20],
        }"""


def get_game(date_slug, competition_slug, teams_slug):
    """
    Games carry no stored slug, so match the derived one within the date and
    the competition -- three games on an average date, thirty-seven on the
    busiest.
    """
    games = Game.objects.filter(competition__slug=competition_slug).select_related(
        'team1', 'team2', 'competition')

    if date_slug == 'no-date':
        games = games.filter(date=None)
    else:
        try:
            games = games.filter(date=datetime.date.fromisoformat(date_slug))
        except ValueError:
            raise Http404("no game dated %s" % date_slug)

    for game in games:
        if game.slug == teams_slug:
            return game

    raise Http404("no game %s" % teams_slug)


def game_detail(request, date_slug, competition_slug, teams_slug):
    game = get_game(date_slug, competition_slug, teams_slug)
    context = {
        'game': game,
        'goals': game.goal_set.order_by('minute'),
        'game_sources': GameSource.objects.filter(game=game),

        }
    return render(request, "games/detail.html",
                              context)




def random_game_detail(request):
    """
    Redirect rather than render, so the reader lands on the game's own url and
    can link to what they got.
    """
    return redirect(Game.objects.select_related(
        'team1', 'team2', 'competition').order_by('?').first())


