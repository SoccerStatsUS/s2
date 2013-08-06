
from django.db.models import Sum, Avg
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from competitions.forms import CompetitionForm
from competitions.models import Competition, Season
from lineups.models import Appearance
from places.models import Country
from stats.models import Stat, CompetitionStat, SeasonStat

from collections import Counter, defaultdict
import json
import datetime

@cache_page(60 * 60 * 12)
def competition_index(request):

    ctype = None

    if request.method == 'GET':
        form = CompetitionForm(request.GET)

        if form.is_valid():
            competitions = Competition.objects.all()

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

            # No changes have been made; use standard competition filter.
            # is_valid() method isn't working because all fields are optional.
            if competitions.count() == Competition.objects.count():
                #competitions = Competition.objects.filter(level=1)
                slugs = ['american-league-of-professional-football',
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
                         ]
                competitions = Competition.objects.filter(slug__in=slugs)

            #international = form.cleaned_data['international']
            #if international is not None:
            #    competitions = competitions.filter(international=international)

        else:
            raise
            form = CompetitionForm()
    
    else:
        raise
        form = CompetitionForm()
            
    # Add a paginator.

    context = {
        'competitions': competitions.select_related(),
        'form': form,
        'ctype': ctype,
        #'itype': itype,
        #'valid': form.is_valid(),
        #'errors': form.errors,

        }
    return render_to_response("competitions/index.html",
                              context,
                              context_instance=RequestContext(request))




@cache_page(60 * 60 * 12)
def competition_detail(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    games = competition.game_set.all()

    stats = CompetitionStat.objects.filter(competition=competition)
    if stats.exclude(games_played=None).exists():
        sx = stats.exclude(games_played=None).order_by('-games_played', '-goals')[:25]
    else:
        sx = stats.exclude(games_played=None, goals=None).filter(competition=competition).order_by('-games_played', '-goals')[:25]

    recent_games = games.order_by('-date').exclude(date__gte=datetime.date.today())
    if not recent_games.exists():
        recent_games = games.order_by('-date')



    context = {
        'competition': competition,
        'stats': sx,
        'games': recent_games.select_related()[:25],
        'big_winners': competition.alltime_standings().order_by('-wins')[:50],
        
        }
    return render_to_response("competitions/competition/detail.html",
                              context,
                              context_instance=RequestContext(request))



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

    return render_to_response("competitions/competition/stats.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def competition_games(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    context = {
        'competition': competition,
        'games': competition.game_set.order_by('season', 'date', 'round'),

        }
    return render_to_response("competitions/competition/games.html",
                              context,
                              context_instance=RequestContext(request))




@cache_page(60 * 60 * 12)
def competition_attendance(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)

    attendance_data = [(e.name, e.average_attendance(), e.total_attendance()) for e in competition.season_set.all()]

    attendance = defaultdict(int)
    agames = defaultdict(int)
    for t, a in competition.game_set.exclude(home_team=None).exclude(attendance=None).values_list('home_team__name', 'attendance'):
        attendance[t] += a
        agames[t] += 1

    team_data = sorted([(k, attendance[k] / agames[k], attendance[k]) for k in agames.keys()])

    games = competition.game_set.exclude(attendance=None)
    top_attendance_games = games.order_by('-attendance')[:10]

    context = {
        'competition': competition,
        'attendance_data': json.dumps(attendance_data),
        'team_data': json.dumps(team_data),
        'top_attendance_games': top_attendance_games,
        'worst_attendance_games': games.exclude(id__in=top_attendance_games.values_list('id', flat=True)).order_by('attendance')[:10],

        }
    return render_to_response("competitions/competition/attendance.html",
                              context,
                              context_instance=RequestContext(request))



@cache_page(60 * 60 * 12)
def season_detail(request, competition_slug, season_slug):
    """
    Detail for a given season, e.g. Major League Soccer, 1996.
    """

    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season, competition=season.competition)
    if stats.exclude(minutes=None).exists():
        stats = stats.exclude(minutes=None).order_by('-minutes')
    elif stats.exclude(games_played=None).exists():
        stats = stats.exclude(games_played=None).order_by('-games_played')
    elif stats.exclude(goals=None).exists():
        stats = stats.exclude(goals=None).order_by('-goals')
    else:
        pass


    bios = Bio.objects.filter(id__in=stats.values_list('player'))
    nationality_count_dict = Counter(bios.exclude(birthplace__country=None).values_list('birthplace__country'))

    # Compute average attendance.
    games = season.game_set.exclude(attendance=None)
    attendance_game_count = games.count()
    average_attendance = games.aggregate(Avg('attendance'))['attendance__avg']

    goal_leaders = stats.exclude(goals=None).order_by('-goals')
    game_leaders = stats.exclude(games_played=None).order_by('-games_played')


    recent_games = season.game_set.exclude(date__gte=datetime.date.today()).order_by('-date')
    if not recent_games.exists():
        recent_games = season.game_set.order_by('-date')

    

    context = {
        'season': season,
        'standings': season.standing_set.filter(final=True),
        'stats': stats[:25],
        'goal_leaders': goal_leaders[:10],
        'game_leaders': game_leaders[:10],
        'average_attendance': average_attendance,
        'attendance_game_count': attendance_game_count,
        'recent_games': recent_games[:25],
        'awards': season.awarditem_set.order_by('award'),
        'stats_nationality_info': json.dumps(season.stats_nationality_info()),
        
        }
    return render_to_response("competitions/season/detail.html",
                              context,
                              context_instance=RequestContext(request))



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
    return render_to_response("competitions/level_detail.html",
                              context,
                              context_instance=RequestContext(request))



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
    return render_to_response("competitions/season/stats.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def season_games(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    context = {
        'season': season,
        'games': competition.game_set.filter(season=season).order_by('date', 'round'),
        }

    return render_to_response("competitions/season/games.html",
                              context,
                              context_instance=RequestContext(request))



@cache_page(60 * 60 * 12)
def season_attendance(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    games = season.game_set.exclude(attendance=None)
    top_attendance_games = games.exclude(attendance=None).order_by('-attendance')[:10]


    attendance = defaultdict(int)
    agames = defaultdict(int)
    for t, a in season.game_set.exclude(home_team=None).exclude(attendance=None).values_list('home_team__name', 'attendance'):
        attendance[t] += a
        agames[t] += 1

    team_data = sorted([(k, attendance[k] / agames[k]) for k in agames.keys()])

    context = {
        'season': season,
        'team_data': json.dumps(team_data),
        'top_attendance_games': top_attendance_games,
        'worst_attendance_games': games.exclude(attendance=None).exclude(id__in=top_attendance_games.values_list('id', flat=True)).order_by('attendance')[:10],
        'stadium_attendance': json.dumps(season.stadium_attendance()),
        'team_attendances': json.dumps(season.total_attendances()),
        }

    return render_to_response("competitions/season/attendance.html",
                              context,
                              context_instance=RequestContext(request))




@cache_page(60 * 60 * 12)
def season_goals(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    from goals.models import Goal

    context = {
        'season': season,
        'goals': Goal.objects.filter(game__season=season).order_by('date', 'team', 'minute'),
        'goal_distribution': json.dumps(season.goal_distribution().items()),
        }

    return render_to_response("competitions/season/goals.html",
                              context,
                              context_instance=RequestContext(request))





@cache_page(60 * 60 * 12)
def season_salaries(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)
    
    player_ids = season.stat_set.values_list('player', flat=True)

    from money.models import Salary
    salaries = Salary.objects.filter(season=season.name).filter(person__in=player_ids)

    context = {
        'season': season,
        'salary_data': salaries.values_list('person__name', 'amount'),
        }

    return render_to_response("competitions/season/salaries.html",
                              context,
                              context_instance=RequestContext(request))




def get_confederation_distribution(stat_qs):
    d = defaultdict(int)
    for gp, country in stat_qs.exclude(player__birthplace__country=None).values_list('games_played', 'player__birthplace__country__confederation'):
        d[country] += gp
    return sorted(d.items(), key=lambda e: -e[1])
        
    
def get_age_counts(l):
    total = 0
    d = defaultdict(int)
    for e in l:
        d[round(e)] += 1
        total += 1

    ftotal = float(total)
    return sorted([(e[0], e[1] / ftotal) for e in d.items()])
    


@cache_page(60 * 60 * 12)
def season_graphs(request, competition_slug, season_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season).exclude(games_played=None)
    #country_dict = Country.objects.id_dict()
    nationality_map = get_confederation_distribution(stats)    
    #nationality_map = [(country_dict[a], b) for (a, b) in nationality_id_map]

    appearance_ages = Appearance.objects.filter(game__season=season).exclude(age=None).values_list('age', 'game__date')
    earliest_date = min([e[1] for e in appearance_ages])

    age_counts = get_age_counts([e[0] for e in appearance_ages])

    
    
    context = {
        'season': season,
        'nationality_map': json.dumps(nationality_map),
        'appearance_ages': json.dumps([(a, (b - earliest_date).days) for (a, b) in appearance_ages]),
        'age_counts': json.dumps(age_counts),

        }
    return render_to_response("competitions/season/graphs.html",
                              context,
                              context_instance=RequestContext(request))




def season_names(request):
    """
    Show the set of all distinct season names.
    """
    
    names = [e[0] for e in Season.objects.values_list('name')]
    names = sorted(set(names))

    context = {
        'names': names,
        }
    
    return render_to_response("competitions/season/names.html",
                              context,
                              context_instance=RequestContext(request))

    

def season_list(request, season_slug):
    """
    List all seasons of with a given slug.
    """

    seasons = Season.objects.filter(slug=season_slug)

    context = {
        'season_exists': seasons.exists(),
        'seasons': seasons,
        }

    return render_to_response("competitions/season/list.html",
                              context,
                              context_instance=RequestContext(request))




