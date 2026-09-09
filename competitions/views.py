
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.cache import cache_page

from django.contrib.contenttypes.models import ContentType

from awards.models import Award, AwardItem
from bios.models import Bio
from competitions.forms import CompetitionForm
from competitions.models import PLAYOFF_CHAMPIONSHIPS, Competition, SuperSeason, Season
from goals.models import Goal
from lineups.models import Appearance
from places.models import Country, playing_time_by_country
from standings.models import Standing
from stats.models import Stat, CompetitionStat, GameStat, SeasonStat
from teams.models import Team

from collections import Counter, defaultdict
import json
import datetime
import statistics

DEFAULT_SLUGS = [
    'american-league-of-professional-football',
    'american-soccer-league-1921-1933',
    'concacaf-champions-league',
    'fifa-club-world-cup',
    'fifa-world-cup',
    'major-league-soccer',
    'north-american-soccer-league',
    'liga-mx',
    'copa-america',
    'mls-cup-playoffs',
    'copa-libertadores',
    'us-open-cup',
    'concacaf-championship',
    'gold-cup',
    'national-womens-soccer-league',
    'olympic-games',
    'womens-united-soccer-association',
    'womens-professional-soccer',
    'premier-league',
]


@cache_page(60 * 60 * 12)
def competition_index(request):

    form = CompetitionForm(request.GET)
    competitions = Competition.objects.all()
    ctype = None

    if form.is_valid():
        level = form.cleaned_data['level']
        if level:
            competitions = competitions.filter(level=level)

        ctype = form.cleaned_data['ctype']
        if ctype:
            competitions = competitions.filter(ctype=ctype)

        area = form.cleaned_data['area']
        if area:
            competitions = competitions.filter(area=area)

        code = form.cleaned_data['code']
        if code:
            competitions = competitions.filter(code=code)

    # No filter applied (or an invalid one): show the standard set.
    if competitions.count() == Competition.objects.count():
        competitions = Competition.objects.filter(slug__in=DEFAULT_SLUGS)

    # Add a paginator.

    context = {
        'competitions': competitions.select_related(),
        'form': form,
        'ctype': ctype,
        #'itype': itype,
        #'valid': form.is_valid(),
        #'errors': form.errors,

        }
    return render(request, "competitions/index.html",
                              context)




def most_titled(competition):
    """
    The club or country with the most championships and how many, or None where
    no champion is on record. Leagues whose title is decided in a separate
    playoffs take their champions from there, matched by season name.
    """
    playoff_slug = PLAYOFF_CHAMPIONSHIPS.get(competition.slug)
    items = AwardItem.objects.filter(award__type='champion')
    if playoff_slug:
        items = items.filter(season__competition__slug=playoff_slug,
                             season__name__in=competition.season_set.values('name'))
    else:
        items = items.filter(season__competition=competition)

    top = (items.values('content_type_id', 'object_id')
           .annotate(titles=Count('id')).order_by('-titles').first())
    if not top:
        return None

    content_type = ContentType.objects.get_for_id(top['content_type_id'])
    try:
        winner = content_type.get_object_for_this_type(id=top['object_id'])
    except content_type.model_class().DoesNotExist:
        return None

    return {'winner': winner, 'titles': top['titles']}


def club_seasons(competition):
    """
    Which clubs played in which seasons, read off the games rather than the
    standings so a competition that keeps no table still counts. Returns the
    season names in season order and a {(name, slug): {season names}} map.
    """
    seasons = [season.name for season in competition.season_set.all()]
    known = set(seasons)
    clubs = {}
    for season, home, home_slug, away, away_slug in competition.game_set.exclude(
            not_played=True).values_list('season__name', 'team1__name', 'team1__slug',
                                         'team2__name', 'team2__slug'):
        if season not in known:
            continue
        for name, slug in ((home, home_slug), (away, away_slug)):
            if name:
                clubs.setdefault((name, slug), set()).add(season)
    return seasons, clubs


def season_club_counts(competition, seasons, clubs, slugs=None):
    """
    How many clubs each season fielded, in season order, each linking to the
    season it counts.
    """
    slugs = slugs or {}
    counts = Counter()
    for played in clubs.values():
        counts.update(played)

    rows = []
    for season in seasons:
        if not counts[season]:
            continue
        url = None
        if season in slugs:
            url = reverse('season_detail', args=[competition.slug, slugs[season]])
        rows.append({'name': season, 'count': counts[season], 'url': url})
    return rows


def club_timeline(competition, seasons, clubs, slugs=None):
    """
    One row per club, last season first so the clubs that lasted lead, and the
    longest-lived first among those that left together.

    Leagues only. A league has a roll of member clubs that returns year on year,
    which is the thing the chart draws; a cup is a field that one-off entrants
    pass through, and the U.S. Open Cup's 1,384 of them would draw a mile of
    single blocks. Empty, too, for a competition with no season structure.
    """
    if competition.ctype != 'League' or len(seasons) < 2 or len(clubs) < 2:
        return {'columns': [], 'rows': []}

    slugs = slugs or {}
    order = {name: index for index, name in enumerate(seasons)}
    rows = []
    for (name, slug), played in clubs.items():
        indexes = sorted(order[season] for season in played)
        # A block links to that club's season in this competition, where there
        # is a slug for both ends of it to build the URL from.
        urls = {season: reverse('team_season_detail',
                                args=[slug, competition.slug, slugs[season]])
                for season in played if slug and season in slugs}
        rows.append({
            'name': name,
            'url': reverse('team_detail', args=[slug]) if slug else None,
            'seasons': played,
            'urls': urls,
            'first': seasons[indexes[0]],
            'last': seasons[indexes[-1]],
            'played': len(played),
            })

    rows.sort(key=lambda row: (-order[row['last']], -row['played'], row['name']))
    return {'columns': seasons, 'rows': rows}


def competition_summary(competition, clubs):
    """
    The facts above the fold. Every one is read off the record rather than
    asserted: what kind of competition this is, the span of seasons on file,
    and the totals behind the tabs below. A competition counts as still played
    when a game is on record from last year or later, which keeps a league
    between seasons out of the past tense.
    """
    games = competition.game_set.exclude(date=None)
    last_game = games.order_by('-date').first()
    crowds = competition.game_set.exclude(attendance=None)

    return {
        'kind': competition.kind(),
        'active': games.filter(date__year__gte=datetime.date.today().year - 1).exists(),
        'last_year': last_game.date.year if last_game else None,
        'seasons': competition.season_set.count(),
        'first_season': competition.first_season(),
        'last_season': competition.last_season(),
        'games': competition.game_set.count(),
        # Counted off the games, the same way the clubs timeline counts them, so
        # the header and the chart below it never disagree.
        'clubs': len(clubs),
        'most_titled': most_titled(competition),
        'attendance': crowds.aggregate(Avg('attendance'))['attendance__avg'],
        }


@cache_page(60 * 60 * 12)
def competition_detail(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    games = competition.game_set.all()

    stats = CompetitionStat.objects.filter(competition=competition)

    recent_games = games.order_by('-date').exclude(date__gte=datetime.date.today()).exclude(date=None)
    if not recent_games.exists():
        recent_games = games.order_by('-date')

    seasons, clubs = club_seasons(competition)
    season_slugs = dict(competition.season_set.values_list('name', 'slug'))

    context = {
        'competition': competition,
        'summary': competition_summary(competition, clubs),
        'leader_groups': player_leader_groups(stats),
        'games': recent_games.select_related()[:25],
        'big_winners': competition.alltime_standings().order_by('-wins')[:50],
        'awards': competition_awards(competition),
        'season_clubs': season_club_counts(competition, seasons, clubs, season_slugs),
        'club_timeline': club_timeline(competition, seasons, clubs, season_slugs),
        'club_noun': 'teams' if competition.international else 'clubs',
        }
    return render(request, "competitions/competition/detail.html",
                              context)


def competition_awards(competition):
    """
    One row per award, with the most recent winner where the award has a single
    winner per season. Awards still being given lead: most recent season first,
    then most winners, then the award's name.
    """
    rows = []
    for award in Award.objects.filter(competition=competition).order_by('name'):
        items = list(award.awarditem_set.select_related('season'))
        if not items:
            continue

        def key(item):
            return (item.season.order if item.season and item.season.order is not None else -1,
                    item.year or 0)

        items.sort(key=key)
        shared = len([item for item in items if key(item) == key(items[-1])]) > 1
        last_order, last_year = key(items[-1])

        rows.append(((-last_order, -last_year, -len(items), award.name), {
            'award': award,
            'count': len(items),
            'first_season': items[0].season,
            'last_season': items[-1].season,
            'latest': None if shared else items[-1],
            }))
    return [row for _, row in sorted(rows, key=lambda pair: pair[0])]



def random_competition_detail(request):
    import random
    competitions = Competition.objects.count()
    c_id = random.randint(1, competitions)
    c_slug = Competition.objects.get(id=c_id).slug
    return redirect('competition_detail', competition_slug=c_slug)
    #return competition_detail(request, c_slug)


@cache_page(60 * 60 * 12)
def competition_stats(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    stats = CompetitionStat.objects.filter(competition=competition).order_by('-games_played').exclude(games_played=None)
    if not stats.exists():
        stats = CompetitionStat.objects.filter(competition=competition).order_by('-goals')

    context = {
        'competition': competition,
        'stats': stats,
        }

    return render(request, "competitions/competition/stats.html",
                              context)


@cache_page(60 * 60 * 12)
@cache_page(60 * 60 * 12)
def competition_games(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    games = competition.game_set.order_by('season', 'date', 'round') \
        .select_related().prefetch_related('sources')
    page = Paginator(games, 500).get_page(request.GET.get('page'))

    context = {
        'competition': competition,
        'games': page.object_list,
        'page': page,
        }
    return render(request, "competitions/competition/games.html",
                              context)



@cache_page(60 * 60 * 12)
def competition_vs(request, competition_slug, competition2_slug):
    c1 = get_object_or_404(Competition, slug=competition_slug)
    c2 = get_object_or_404(Competition, slug=competition2_slug)

    s1 = set(Stat.objects.filter(competition=c1).values_list('player', flat=True))
    s2 = set(Stat.objects.filter(competition=c2).values_list('player', flat=True))

    both = Bio.objects.filter(id__in=s1.intersection(s2)).order_by('name')

    cd1 = dict([(e.player, e) for e in CompetitionStat.objects.filter(competition=c1, player__id__in=both).order_by('player')])
    cd2 = dict([(e.player, e) for e in CompetitionStat.objects.filter(competition=c2, player__id__in=both).order_by('player')])

    z = [(e, cd1.get(e), cd2.get(e)) for e in both]

    context = {
        'competition1': c1,
        'competition2': c2,
        'players': both,
        'zipped': z,
        'c1': cd1,
        'c2': cd2,
        }
    return render(request, "competitions/competition/vs.html",
                              context)




def attendance_by_home_club(crowds):
    """
    Average and median home crowd per club, largest average first, over games
    whose source said who was at home. Games without that are counted and
    reported as left out, never guessed from listing order.
    """
    by_team = defaultdict(list)
    for team_id, attendance in crowds.exclude(neutral=True).exclude(home_team=None).values_list('home_team_id', 'attendance'):
        by_team[team_id].append(attendance)
    teams = {t.id: t for t in Team.objects.filter(id__in=by_team)}
    clubs = sorted([{
        'name': teams[tid].name,
        'url': teams[tid].get_absolute_url(),
        'games': len(crowd),
        'total': sum(crowd),
        'average': statistics.fmean(crowd),
        'median': statistics.median(crowd),
    } for tid, crowd in by_team.items()], key=lambda r: -r['average'])
    return clubs, crowds.count() - sum(len(crowd) for crowd in by_team.values())


def show_club_table(clubs, charted_clubs):
    """
    The club table earns its place only where the chart cannot stand alone:
    too few clubs for bar_chart to draw one, or clubs it leaves out. Where the
    chart carries every club the table only repeats it.
    """
    return len(charted_clubs) < 3 or len(charted_clubs) != len(clubs)


@cache_page(60 * 60 * 12)
def competition_attendance(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    played = competition.game_set.exclude(not_played=True)
    crowds = played.exclude(attendance=None)

    # By season, in season order. Seasons without a game are left out; seasons
    # without a crowd keep their slot so the chart's timeline stays continuous.
    games_by_season = dict(played.values_list('season_id').annotate(n=Count('id')))
    crowds_by_season = defaultdict(list)
    for season_id, attendance in crowds.values_list('season_id', 'attendance'):
        crowds_by_season[season_id].append(attendance)

    seasons = []
    for season in competition.season_set.all():
        games = games_by_season.get(season.id, 0)
        if not games:
            continue
        crowd = crowds_by_season.get(season.id, [])
        seasons.append({
            'name': season.name,
            'url': reverse('season_attendance', args=[competition.slug, season.slug]),
            'games': games,
            'known': len(crowd),
            'partial': len(crowd) < games / 2,
            'average': statistics.fmean(crowd) if crowd else None,
            'median': statistics.median(crowd) if crowd else None,
            'total': sum(crowd) if crowd else None,
            'largest': max(crowd) if crowd else None,
        })

    clubs, unattributed = attendance_by_home_club(crowds)
    charted_clubs = [c for c in clubs if c['games'] >= 10]
    largest = crowds.order_by('-attendance').select_related()[:10]
    smallest = crowds.exclude(id__in=largest.values_list('id', flat=True)).order_by('attendance').select_related()[:10]

    context = {
        'competition': competition,
        'games': played.count(),
        'known': crowds.count(),
        'total': crowds.aggregate(Sum('attendance'))['attendance__sum'],
        'average': crowds.aggregate(Avg('attendance'))['attendance__avg'],
        'seasons': seasons,
        'clubs': clubs,
        'charted_clubs': charted_clubs,
        'show_club_table': show_club_table(clubs, charted_clubs),
        'unattributed': unattributed,
        'largest': largest,
        'smallest': smallest,
    }
    return render(request, "competitions/competition/attendance.html", context)


# The coverage columns, in table order. Each is a share of the season's played
# games except goals, which is a share of the goals those games are recorded as
# having produced. 'view' names the season page that shows the data itself; the
# key doubles as the column heading.
COVERAGE_FACETS = [
    {'key': 'results', 'view': 'season_games'},
    {'key': 'goals', 'view': 'season_goals'},
    {'key': 'lineups', 'view': 'season_detail'},
    {'key': 'stats', 'view': 'season_stats'},
    {'key': 'attendance', 'view': 'season_attendance'},
    {'key': 'venue', 'view': 'season_games'},
    {'key': 'referee', 'view': 'season_games'},
]


def coverage_counts(competition):
    """
    What the database holds for each season of a competition, counted in five
    aggregate passes rather than a query per season per facet. Keyed by season
    id; a season with nothing on record is absent from every dict.

    Games not played are left out of every count. They are a recorded fact, not
    a gap, and counting them would make a cancelled season look unsourced.
    """
    played = Q(not_played=False)

    games = {row.pop('season_id'): row for row in competition.game_set.values('season_id').annotate(
        played=Count('id', filter=played),
        results=Count('id', filter=played & ~Q(team1_result='')),
        attendance=Count('id', filter=played & Q(attendance__isnull=False)),
        venue=Count('id', filter=played & Q(stadium__isnull=False)),
        referee=Count('id', filter=played & Q(referee__isnull=False)),
        scored=Sum('goals', filter=played),
    )}

    # Lineups and stats are per player, so count the distinct games they cover;
    # goals are the itemized total to set against the goals the games scored.
    lineups = dict(Appearance.objects.filter(game__competition=competition)
                   .values_list('game__season_id').annotate(n=Count('game_id', distinct=True)))
    stats = dict(GameStat.objects.filter(game__competition=competition)
                 .values_list('game__season_id').annotate(n=Count('game_id', distinct=True)))
    goals = dict(Goal.objects.filter(game__competition=competition)
                 .values_list('game__season_id').annotate(n=Count('id')))

    # A season's standings are held either as the final table or as dated
    # in-season snapshots, and the two are worth telling apart: most seasons
    # here have the running tables but never had a final one transcribed, and
    # reporting that as "no standings" would understate what is on file.
    tables = {}
    for season_id, final in Standing.objects.filter(
            season__competition=competition).values_list('season_id', 'final').distinct():
        if final or season_id not in tables:
            tables[season_id] = 'final' if final else 'dated'

    return {'games': games, 'lineups': lineups, 'stats': stats,
            'goals': goals, 'tables': tables}


def coverage_cell(known, total, url=None):
    """
    One cell of the coverage table, in the three states DESIGN.md §9 asks to be
    told apart: a figure, nothing on record, and nothing to have a record of.
    A cell with nothing in it carries no link, only the marker.
    """
    if not total:
        return {'state': 'no-games', 'share': None, 'known': known, 'total': total, 'url': None}
    if not known:
        return {'state': 'none', 'share': 0, 'known': 0, 'total': total, 'url': None}

    # A game whose goals are itemized more completely than its score was
    # recorded would read as more than complete; report it as complete. At the
    # other end, a share that rounds to nothing is not nothing -- MLS 2012 has
    # one refereed game in 323 -- so it keeps its own reading rather than
    # rendering as the 0% that a reader would take for a gap.
    share = min(100, round(100 * known / total))
    return {'state': 'have', 'share': share, 'known': known, 'total': total,
            'url': url, 'trace': share == 0}


def coverage_rows(competition, seasons, counts):
    """
    A row per season, newest first, and a totals row across all of them.
    """
    rows = []
    totals = defaultdict(int)
    for season in seasons:
        games = counts['games'].get(season.id, {})
        played = games.get('played', 0)
        scored = games.get('scored') or 0
        known = {
            'results': (games.get('results', 0), played),
            'goals': (counts['goals'].get(season.id, 0), scored),
            'lineups': (counts['lineups'].get(season.id, 0), played),
            'stats': (counts['stats'].get(season.id, 0), played),
            'attendance': (games.get('attendance', 0), played),
            'venue': (games.get('venue', 0), played),
            'referee': (games.get('referee', 0), played),
        }

        cells = []
        for facet in COVERAGE_FACETS:
            have, total = known[facet['key']]
            url = reverse(facet['view'], args=[competition.slug, season.slug]) if have else None
            cells.append(coverage_cell(have, total, url))
            totals[facet['key']] += have
            totals[facet['key'] + '_total'] += total

        totals['played'] += played
        rows.append({
            'name': season.name,
            'url': reverse('season_detail', args=[competition.slug, season.slug]),
            'played': played,
            'cells': cells,
            'table': counts['tables'].get(season.id),
            })

    total_row = {
        'played': totals['played'],
        'cells': [coverage_cell(totals[f['key']], totals[f['key'] + '_total'])
                  for f in COVERAGE_FACETS],
        'finals': len([kind for kind in counts['tables'].values() if kind == 'final']),
        'seasons': len(rows),
        }
    rows.reverse()
    return rows, total_row


def missing_years(seasons):
    """
    Years inside the recorded span with no season on file — the NWSL's 2020,
    whose regular season was never played. Only competitions whose seasons are
    all named for a single year can be read this way; a split-year league gets
    nothing rather than a wrong answer.
    """
    years = []
    for season in seasons:
        if not season.name.isdigit() or len(season.name) != 4:
            return []
        years.append(int(season.name))

    if len(years) < 2:
        return []
    return [year for year in range(min(years), max(years) + 1) if year not in set(years)]


@cache_page(60 * 60 * 12)
def competition_coverage(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    seasons = list(competition.season_set.all())
    rows, totals = coverage_rows(competition, seasons, coverage_counts(competition))

    context = {
        'competition': competition,
        'facets': COVERAGE_FACETS,
        'rows': rows,
        'totals': totals,
        'missing_years': missing_years(seasons),
        }
    return render(request, "competitions/competition/coverage.html", context)


@cache_page(60 * 60 * 12)
def superseason_detail(request, superseason_slug):

    ss = get_object_or_404(SuperSeason, slug=superseason_slug)

    context = {
        'superseason': ss,
        }
    

    return render(request, "competitions/superseason/detail.html",
                              context)


@cache_page(60 * 60 * 12)
def season_detail(request, competition_slug, season_slug):
    """
    Detail for a given season, e.g. Major League Soccer, 1996.
    """

    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season, competition=season.competition)

    # Compute average attendance.
    games = season.game_set.exclude(attendance=None)
    attendance_game_count = games.count()
    average_attendance = games.aggregate(Avg('attendance'))['attendance__avg']

    recent_games = season.game_set.exclude(date__gte=datetime.date.today()).order_by('-date')
    if not recent_games.exists():
        recent_games = season.game_set.order_by('-date')

    

    context = {
        'season': season,
        'standings': season_standings(season),
        'leader_groups': player_leader_groups(stats),
        'average_attendance': average_attendance,
        'attendance_game_count': attendance_game_count,
        'recent_games': recent_games[:25],
        'honors': season_honors(season),
        'awards': season.awarditem_set.order_by('award'),
        'postseason': season_postseason(season),
        'origins': playing_time_by_country(stats),
        }
    return render(request, "competitions/season/detail.html",
                              context)


def season_standings(season):
    standings = list(season.standing_set.filter(final=True).select_related('team')
                     .order_by('-points', '-wins', 'team__name'))
    team_names = defaultdict(Counter)

    for team1_id, team1_name, team2_id, team2_name in season.game_set.values_list(
            'team1_id', 'team1_original_name', 'team2_id', 'team2_original_name'):
        if team1_name:
            team_names[team1_id][team1_name] += 1
        if team2_name:
            team_names[team2_id][team2_name] += 1

    for standing in standings:
        names = team_names[standing.team_id]
        standing.team_display_name = names.most_common(1)[0][0] if names else standing.team.name

    return standings


# Goals, assists and appearances. Minutes ranks the same players as
# appearances and reads as a bigger number for it, so it earns no column.
LEADER_CATEGORIES = (
    ('Goals', 'goals'),
    ('Assists', 'assists'),
    ('Appearances', 'games_played'),
)

LEADER_DEPTH = 10


def player_leader_groups(stats):
    """
    Career leaders for a competition or a club, the same shape either way so
    the two stats tabs read alike.
    """
    groups = []
    for label, field in LEADER_CATEGORIES:
        rows = list(stat_leaders(stats, field))
        if rows:
            groups.append({'label': label, 'rows': rows})
    return groups


def stat_leaders(stats, field):
    return (stats.filter(**{f'{field}__gt': 0})
            .values('player_id', 'player__name', 'player__slug')
            .annotate(value=Sum(field))
            .order_by('-value', 'player__name')[:LEADER_DEPTH])


def season_postseason(season):
    playoff_slug = PLAYOFF_CHAMPIONSHIPS.get(season.competition.slug)
    if not playoff_slug:
        return None

    playoff_season = (Season.objects
                      .filter(super_season=season.super_season,
                              competition__slug=playoff_slug)
                      .select_related('competition')
                      .first())
    if not playoff_season:
        return None

    championship_game = (playoff_season.game_set
                         .filter(round__in=('MLS Cup', 'Final', 'Championship'),
                                 not_played=False)
                         .select_related('team1', 'team2', 'competition')
                         .order_by('-date', '-id')
                         .first())
    if not championship_game and playoff_season.champion():
        championship_game = (playoff_season.game_set
                             .exclude(date=None)
                             .exclude(not_played=True)
                             .select_related('team1', 'team2', 'competition')
                             .order_by('-date', '-id')
                             .first())
    return {'season': playoff_season, 'championship_game': championship_game}


def season_honors(season):
    """
    Champion, any secondary title (Supporters' Shield and the like), mvp and
    golden boot, flattened into rows so the template does not have to know that
    they come from three different places.
    """
    rows = []

    def add(label, recipient, note=None):
        rows.append({'label': label, 'recipient': recipient, 'note': note})

    champion = season.champion()
    if champion and champion.award.competition_id != season.competition_id:
        # Decided in a separate playoff competition, so name the trophy.
        add('champion', champion.recipient, champion.award.name)
    else:
        add('champion', champion.recipient if champion else None)

    others = AwardItem.objects.filter(season=season, award__type='champion').select_related('award')
    for item in others:
        if champion and item.id == champion.id:
            continue
        add(item.award.name.lower(), item.recipient)

    mvp = season.mvp()
    add('mvp', mvp.recipient if mvp else None)

    add('golden boot', season.golden_boot())

    return rows



@cache_page(60 * 60 * 12)
def season_date_detail(request, competition_slug, season_slug, year, month, day):
    """
    Summarize the events of the day for the season.
    """

    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    d = datetime.date(int(year), int(month), int(day))

    standings = season.standing_set.filter(final=True)
    standings_count = standings.count()
    
    running_standings = []
    team_standing_set = set()



    previous_game = season.standing_set.exclude(final=True).exclude(date__gt=d).order_by('-date')
    if previous_game.exists():
        previous_date = previous_game[0].date
    else:
        previous_date = None

    next_game = season.standing_set.exclude(final=True).exclude(date__lt=d).order_by('date')
    if next_game.exists():
        next_date = next_game[0].date
    else:
        next_date = None

    xstandings = season.standing_set.exclude(final=True).filter(date__lte=d).order_by('date')

    for e in xstandings:
        if e.team not in team_standing_set:
            running_standings.append(e)
            team_standing_set.add(e.team)
        
        if len(team_standing_set) == standings_count:
            break

    games = season.game_set.filter(date=d)

    context = {
        'standings': running_standings,
        'date': d,
        'games': games,
        'previous_date': previous_date,
        'next_date': next_date,
        'season': season,
        }

    return render(request, "competitions/season/date.html",
                              context)



@cache_page(60 * 60 * 12)
def level_detail(request, level_slug):
    from games.models import Game
    from standings.models import Standing

    stats = CompetitionStat.objects.filter(competition__level=level_slug)

    goal_leaders = stats.order_by('-goals')
    game_leaders = stats.order_by('-games_played')




    context = {
        'level': level_slug,
        'stats': stats[:30],
        'games': Game.objects.filter(competition__level=level_slug)[:25],
        'standings': Standing.objects.filter(competition__level=level_slug)[:30],
        'goal_leaders': goal_leaders[:10],
        'game_leaders': game_leaders[:10],
        }
    return render(request, "competitions/level_detail.html",
                              context)



@cache_page(60 * 60 * 12)
def season_stats(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season).order_by('-games_played').exclude(games_played=None)
    if not stats.exists():
        stats = Stat.objects.filter(season=season).order_by('-goals')

    context = {
        'season': season,
        'stats': stats,
        }
    return render(request, "competitions/season/stats.html",
                              context)


@cache_page(60 * 60 * 12)
def season_games(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    context = {
        'season': season,
        'games': competition.game_set.filter(season=season).order_by('date', 'round'),
        }

    return render(request, "competitions/season/games.html",
                              context)


@cache_page(60 * 60 * 12)
def season_attendance(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)
    played = season.game_set.exclude(not_played=True)
    crowds = played.exclude(attendance=None)

    clubs, unattributed = attendance_by_home_club(crowds)
    charted_clubs = [c for c in clubs if c['games'] >= 3]
    largest = crowds.order_by('-attendance').select_related()[:10]
    smallest = crowds.exclude(id__in=largest.values_list('id', flat=True)).order_by('attendance').select_related()[:10]

    context = {
        'competition': competition,
        'season': season,
        'games': played.count(),
        'known': crowds.count(),
        'total': crowds.aggregate(Sum('attendance'))['attendance__sum'],
        'average': crowds.aggregate(Avg('attendance'))['attendance__avg'],
        'clubs': clubs,
        'charted_clubs': charted_clubs,
        'show_club_table': show_club_table(clubs, charted_clubs),
        'unattributed': unattributed,
        'largest': largest,
        'smallest': smallest,
    }
    return render(request, "competitions/season/attendance.html", context)


CEILING = 5  # scores at or above this share a bucket, rendered "5+"


def scoreline_rows(season):
    """
    Every scoreline the season produced, commonest first, home score leading.
    The share is of the games the distribution could read, not of the season --
    neutral-site games have no home side and are not in either figure.
    """
    counts = season.goal_distribution(CEILING)
    total = sum(counts.values())
    if not total:
        return [], 0

    def label(score):
        return "%d+" % score if score >= CEILING else str(score)

    rows = [{'name': "%s-%s" % (label(home), label(away)),
             'count': n,
             'percent': 100.0 * n / total}
            for (home, away), n in counts.items()]
    rows.sort(key=lambda row: (-row['count'], row['name']))
    return rows, total


@cache_page(60 * 60 * 12)
def season_goals(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    rows, read = scoreline_rows(season)

    context = {
        'season': season,
        'scorelines': rows,
        # The chart labels every column, so it takes only as many as it can
        # label; the table under it carries the rest.
        'charted_scorelines': rows[:12],
        'scored_games': read,
        'games': season.game_set.count(),
        }

    return render(request, "competitions/season/goals.html",
                              context)
