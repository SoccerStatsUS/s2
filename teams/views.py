from collections import defaultdict, OrderedDict, Counter
import datetime
import json


from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from competitions.models import Season, Competition
from games.models import Game
from places.models import Country
from positions.models import Position
from teams.forms import TeamGameForm, TeamStatForm
from teams.models import Team
from standings.models import Standing
from stats.models import Stat, TeamStat, CareerStat


class TempGameStanding(object):
    # Use this to generate a standing for a given set of games
    def __init__(self, games, team):
        self.games = games.count()
        self.team = team

        t1_games = games.filter(team1=team)
        t2_games = games.filter(team2=team)

        goals_for = goals_against = 0
        if t1_games.exists():
            gf = t1_games.aggregate(Sum('team1_score'))['team1_score__sum']
            if gf:
                goals_for += gf
            ga = t1_games.aggregate(Sum('team2_score'))['team2_score__sum']
            if ga:
                goals_against += ga

        if t2_games.exists():
            gf = t2_games.aggregate(Sum('team2_score'))['team2_score__sum'] 
            if gf:
                goals_for +=  gf
            ga = t2_games.aggregate(Sum('team1_score'))['team1_score__sum'] 
            if ga:
                goals_against += ga
        
        self.goals_for = goals_for
        self.goals_against = goals_against
        t1_results = [e[0] for e in games.filter(team1=team, team1_result__in='wlt').values_list('team1_result')]
        t2_results = [e[0] for e in games.filter(team2=team, team2_result__in='wlt').values_list('team2_result')]
        results = t1_results + t2_results
        c = Counter(results)
        self.wins, self.ties, self.losses = c['w'], c['t'], c['l']

        if self.games:
            self.win_percentage_100 = 100 * (self.wins + .5 * self.ties) / self.games
        else:
            self.win_percentage_100 = 0





@cache_page(60 * 60 * 12)
def team_index(request):
    """
    Teams shown by letter.
    """
    # This is not good but not sure how to fix.
    # Need to broaden team standing generation so we use that
    # to pull all teams.
    
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    name_dict = OrderedDict()

    standings = Standing.objects.filter(competition=None)

    for letter in letters:
        #teams = Team.objects.filter(name__istartswith=letter)[:10]
        team_standings = standings.filter(team__name__istartswith=letter).order_by('-games')[:10]
        name_dict[letter] = team_standings
        
    context = {
        'name_dict': name_dict,
        }

    return render(request, "teams/index.html",
                              context)


def team_standings(request):

    standings = Standing.objects.filter(competition=None).order_by('-wins')

    context = {
        'standings': standings,
        }

    return render(request, "teams/standings.html",
                              context)




def team_list_generic(request, team_list=None, standing_type=None, ):

    if team_list is None:
        standings = Standing.objects.filter(competition=None).order_by("-wins")[:1000]
    else:
        standings = Standing.objects.filter(competition=None, team__in=team_list).order_by('-wins')

    context =  {
        'standings': standings.select_related(),
        'standing_type': standing_type,
        }
    return render(request, "teams/list.html",
                              context)    


@cache_page(60 * 60 * 12)
def team_name_fragment(request, fragment):
    return team_list_generic(request,
                             Team.objects.filter(name__istartswith=fragment),
                             'alltime')






def seasons_dashboard(request):
    season_names = defaultdict(list)
    for season in Season.objects.all():
        season_names[season.name].append(season)

    context = {
        'season_dict': season_names,
        'seasons': sorted(season_names.keys()),
        }

    return render(request, "teams/seasons.html",
                              context)


    
def team_position_detail(request, team_slug, position_slug):

    team = get_object_or_404(Team, slug=team_slug)
    positions = Position.objects.filter(slug=position_slug, team=team)



    context = {
        'team': team,
        'positions': positions,
        }

    return render(request, "teams/position_detail.html",
                              context)



    

def team_detail(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)
    # Add aliases.

    today = datetime.date.today()

    stats = TeamStat.objects.filter(team=team)
    goal_leaders = game_leaders = None
    if stats.exclude(games_played=None).exists():
        stats = game_leaders = stats.exclude(games_played=None).order_by('-games_played')
        goal_leaders = stats.exclude(goals=None).order_by('-goals')
    elif stats.exclude(goals=None).exists():
        stats = goal_leaders = stats.exclude(goals=None).order_by('-goals')
    else:
        pass


    competition_standings = Standing.objects.filter(team=team, season=None).order_by('-wins')
    league_standings = Standing.objects.filter(team=team, season__competition__ctype='League').filter(final=True).reverse()

    games_count = team.game_set().count()
    dated_games = team.game_set().exclude(date=None).order_by('date')
    first_game = dated_games.first()
    last_game = dated_games.last()
    alltime = Standing.objects.filter(team=team, competition=None, season=None).first()

    recent_games = team.game_set().filter(date__lt=today).order_by('-date').select_related()[:10]
    if recent_games.count() == 0:
        recent_games = team.game_set().select_related()[:10]

    #awards = team.awards.order_by('-season')

    """
    if game_leaders:
        game_leaders = game_leaders[:15]

    if goal_leaders:
        goal_leaders = goal_leaders[:15]
    """


    context = {
        'team': team,
        'recent_games': recent_games,
        'competition_standings': competition_standings,
        'league_standings': league_standings,
        'games_count': games_count,
        'first_game': first_game,
        'last_game': last_game,
        'alltime': alltime,
        'game_leaders': game_leaders,
        'goal_leaders': goal_leaders,
        'gx': True,
        }

    return render(request, "teams/detail.html",
                              context)



def team_competition_detail(request, team_slug, competition_slug):
    team = get_object_or_404(Team, slug=team_slug)
    c = get_object_or_404(Competition, slug=competition_slug)
    games = Game.objects.team_filter(team).filter(competition=c)


    context = {
        'team': team,
        'competition': c,
        'stats': TeamStat.objects.filter(team=team), # Wrong stat for the time being.
        'games': games,
        'result_json': json.dumps([e.result(team) for e in games]), # Probably need to format better than this.
        }

    return render(request, "teams/competition_detail.html",
                              context)



def cumulative_points(gameset, team):
    points = 0
    l = []
    for g in gameset:
        r = g.result(team)
        if r == 'w':
            points += 3
        elif r == 't':
            points += 1

        l.append(points)

    return l


def team_form(gameset, team):
    
    l = []

    for g in gameset:
        l.append(g.margin(team))

    return l
    


def team_season_detail(request, team_slug, competition_slug, season_slug):
    team = get_object_or_404(Team, slug=team_slug)
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)
    games = Game.objects.team_filter(team).filter(season=season)

    points = cumulative_points(games, team)
    
    form_data = team_form(games, team)


    stats = Stat.objects.filter(team=team, season=season)

    goal_scorers = list(stats.exclude(goals=0).values_list('player__name', 'goals'))
    assisters = list(stats.exclude(assists=0).values_list('player__name', 'assists'))

    context = {
        'team': team,
        'season': season,
        'points': json.dumps(points),
        'stats': stats,
        'games': games,
        'result_json': json.dumps([e.result(team) for e in games]), # Probably need to format better than this.
        'form_data': json.dumps(form_data),
        'goal_scorers': json.dumps(goal_scorers),        
        'assisters': json.dumps(assisters),
        }

    return render(request, "teams/season_detail.html",
                              context)

        

def random_team_detail(request):
    import random
    teams = Team.objects.count()
    team_id = random.randint(1, teams)
    team_slug = Team.objects.get(id=team_id).slug
    return team_detail(request, team_slug)

    

def team_stats(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    stats = TeamStat.objects.filter(team=team)

    if request.method == 'GET':
        form = TeamStatForm(team, request.GET)

        if form.is_valid():
            """
            if form.cleaned_data['birthplace']:
                stats = stats.filter(player__birthplace=form.cleaned_data['birthplace'])
                """
            if form.cleaned_data['birth_state']:
                stats = stats.filter(player__birthplace__state=form.cleaned_data['birth_state'])

    else:
        form = TeamStatForm(team)

    context = {
        'form': form,
        'team': team,
        'stats': stats.order_by('-games_played'), #.select_related(),
        }

    return render(request, "teams/stats.html",
                              context)



def team_picks(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    picks = team.pick_set.all()

    player_ids = [e[0] for e in picks.exclude(player=None).values_list('player')]
    #team_stats = Stat.team_stats.filter(team=team, player__in=player_ids)
    career_stats = CareerStat.objects.filter(player__in=player_ids)

    context = {
        'team': team,
        'picks': picks.select_related(),
        'stats': career_stats,
        }

    return render(request, "teams/picks.html",
                              context)



# Duplicate of season.views function.
def get_nationality_distribution(stat_qs):
    d = defaultdict(int)
    for gp, country in stat_qs.exclude(player__birthplace__country=None).values_list('games_played', 'player__birthplace__country'):
        d[country] += gp
    return sorted(d.items(), key=lambda e: -e[1])



def team_graphs(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    stats = TeamStat.objects.filter(team=team).exclude(games_played=None)
    country_dict = Country.objects.id_dict()
    nationality_id_map = get_nationality_distribution(stats)    
    nationality_map = [(country_dict[a], b) for (a, b) in nationality_id_map]


    context = {
        'team': team,
        'nationality_map': json.dumps(nationality_map),
        }

    return render(request, "teams/graphs.html",
                              context)



def team_draftees(request, team_slug):

    team = get_object_or_404(Team, slug=team_slug)

    picks = team.former_team_set.all()

    player_ids = [e[0] for e in picks.exclude(player=None).values_list('player')]
    #team_stats = Stat.team_stats.filter(team=team, player__in=player_ids)
    career_stats = CareerStat.objects.filter(player__in=player_ids)

    context = {
        'team': team,
        'picks': picks.select_related(),
        'stats': career_stats,
        }

    return render(request, "teams/picks.html",
                              context)


    

@cache_page(60 * 24)
def team_games(request, team_slug):
    """
    A filterable table of all games played by a team.
    """
    team = get_object_or_404(Team, slug=team_slug)

    games = Game.objects.team_filter(team)

    if request.method == 'GET':
        form = TeamGameForm(team, request.GET)

        if form.is_valid():

            if form.cleaned_data['opponent']:
                games = Game.objects.team_filter(team, form.cleaned_data['opponent'])
            else:
                games = Game.objects.team_filter(team)

            if form.cleaned_data['competition']:
                games = games.filter(competition=form.cleaned_data['competition'])

            if form.cleaned_data['stadium']:
                games = games.filter(stadium=form.cleaned_data['stadium'])

            r = form.cleaned_data['result']
            if r:
                if r == 't':
                    games = games.filter(team1_result='t')
                else:
                    games = games.filter(Q(team1=team, team1_result=r) | Q(team2=team, team2_result=r))



            if form.cleaned_data['year']:
                year = int(form.cleaned_data['year'])
                games = games.exclude(date=None)
                year_filter = form.cleaned_data['year_filter']
                if year_filter == '>':
                    d = datetime.date(year, 1, 1)
                    games = games.filter(date__gte=d)
                elif year_filter == '<':
                    d = datetime.date(year, 12, 31)
                    games = games.filter(date__lte=d)
                else:
                    games = games.filter(date__year=year)
    else:
        form = TeamGameForm(bio)

    games = games.select_related().order_by('-has_date', '-date', '-season')
    #games = games.select_related().order_by('-date', '-season')
    standings = [TempGameStanding(games, team)]



    context = {
        'team': team,
        'form': form,
        'games': games,
        'standings': standings,
        }

    return render(request, "teams/games.html",
                              context)
    





@cache_page(60 * 24)
def team_calendar(request, team_slug):
    """
    A calendar of a team's games.
    """
    team = get_object_or_404(Team, slug=team_slug)

    games = Game.objects.team_filter(team).select_related().order_by('-has_date', '-date', '-season')

    context = {
        'team': team,
        'games': games,
        }

    return render(request, "teams/calendar.html",
                              context)
    


def team_versus(request, team1_slug, team2_slug):
    """
    Just about the most important view of all.
    """
    team1 = get_object_or_404(Team, slug=team1_slug)
    team2 = get_object_or_404(Team, slug=team2_slug)

    context = {
        'team1': team1,
        'team2': team1,
        'games': Game.objects.team_filter(team1, team2),
        }

    return render(request, "teams/versus.html",
                              context)
    


def team_year_detail(request, team_slug, year):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    seasons = Season.objects.filter(name=year)

    chart_years, chart = team.player_chart(year)

    context = {
        'team': team,
        'year': year,
        'standings': Standing.objects.filter(team=team, season__in=seasons),
        'stats': Stat.objects.filter(team=team, season__in=seasons),
        'games': team.game_set().filter(date__year=year),
        'chart': chart,
        'chart_years': chart_years,
        }

    return render(request, "teams/year_detail.html",
                              context)
    


@cache_page(60 * 24)
def teams_ajax(request):
    PAGE = 0
    ITEMS_PER_PAGE = 100

    def get_stats(request):
        stats = Stat.objects.all().order_by("-minutes")
        if 'team' in request.GET:
            t = request.GET['team']
            stats = stats.filter(team__name__icontains=t)

        if 'season' in request.GET:
            e = request.GET['season']
            stats = stats.filter(season__name__icontains=e)

        if 'name' in request.GET:
            e = request.GET['name']
            stats = stats.filter(player__name__icontains=e)

        if 'competition' in request.GET:
            e = request.GET['competition']
            stats = stats.filter(competition__name__icontains=e)

        return stats

    stats = get_stats(request)

    context = {
        'stats': stats[:1000],
        }

    return render(request, "stats/ajax.html",
                              context)

    


def bad_teams(request):


    
    context = {
        'duplicate_slugs': Team.objects.duplicate_slugs(),
        }

    return render(request, "teams/bad.html",
                              context)    
                              
