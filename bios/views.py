from collections import OrderedDict, Counter
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Substr, Upper
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from games.models import Game
from stats.models import Stat, CareerStat, GameStat

from bios.forms import BioGameStatForm

class AppearanceStat(object):
    def __init__(self, player, game_stats):
        from goals.models import Goal, Assist

        self.player = player

        #self.goals_for = game_stats.exclude(goals_for=None).aggregate(Sum('goals_for'))['goals_for__sum']
        #self.goals_against = game_statsexclude(goals_against=None).aggregate(Sum('goals_against'))['goals_against__sum']
        results = [e[0] for e in game_stats.filter(result__in='wlt').values_list('result')]
        c = Counter(results)
        self.wins, self.ties, self.losses = c['w'], c['t'], c['l']
        self.games = game_stats.count()

        if self.games:
            self.win_percentage_100 =  (self.wins + .5 * self.ties) / self.games
        else:
            self.win_percentage_100 = 0

        #game_ids = game_stats.values_list('game')
        self.games_played = game_stats.filter(games_played=1).count()
        self.games_started = game_stats.filter(games_started=1).count()

        self.minutes = game_stats.exclude(minutes=None).aggregate(Sum('minutes'))['minutes__sum']
        self.goals = game_stats.exclude(goals=None).aggregate(Sum('goals'))['goals__sum']
        self.assists = game_stats.exclude(assists=None).aggregate(Sum('assists'))['assists__sum'] 




def person_list_generic(request, person_list=None):

    if person_list is None:
        stats = CareerStat.objects.all()[:1000]
    else:
        stats = CareerStat.objects.filter(player__in=person_list)

    context =  {
        'stats': stats.select_related(),
        }
    return render(request, "bios/list.html",
                              context)    

        

def one_word(request):
    bios = Bio.objects.exclude(name__contains=' ')
    return person_list_generic(request, bios)
    


@cache_page(60 * 60 * 12)
def person_index(request):

    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()
    stats = CareerStat.objects.order_by(
        '-player__hall_of_fame',
        F('games_played').desc(nulls_last=True)).select_related()

    # One query for every letter's total. Counts CareerStat rows, which is what
    # the name-fragment page lists — not Bio rows, which would overstate it.
    totals = dict(CareerStat.objects
                  .annotate(initial=Upper(Substr('player__name', 1, 1)))
                  .values('initial')
                  .annotate(n=Count('id'))
                  .values_list('initial', 'n'))

    name_dict = OrderedDict()
    for letter in letters:
        name_dict[letter] = {
            'names': stats.filter(player__name__istartswith=letter)[:10],
            'count': totals.get(letter, 0),
            }


    #most_games = CareerStat.objects.exclude(games_played=None).order_by('-games_played')[:25]
    #most_goals = CareerStat.objects.exclude(goals=None).order_by('-goals')[:25]

    context = {
        'name_dict': name_dict,
        #'most_games': most_games,
        #'most_goals': most_goals,
        }

    return render(request, "bios/index.html",
                              context)


@cache_page(60 * 60 * 12)
def bio_name_fragment(request, fragment):
    return person_list_generic(request,
                               Bio.objects.filter(name__istartswith=fragment))


def bios_qa(request):
    """
    Bios sharing a slug. Two bios on one slug means one of them is unreachable:
    the URL serves whichever has the lower id.
    """
    slugs = (Bio.objects.values('slug').annotate(n=Count('id'))
             .filter(n__gt=1).values_list('slug', flat=True))
    groups = OrderedDict()
    for bio in Bio.objects.filter(slug__in=list(slugs)).order_by('slug', 'id'):
        groups.setdefault(bio.slug, []).append(bio)

    context = {
        'groups': list(groups.items()),
        'slug_count': len(groups),
        }

    return render(request, "bios/qa.html",
                              context)
                              


def person_detail(request, slug):
    bio = Bio.objects.by_slug(slug)
    return person_detail_abstract(request, bio)

def person_id_detail(request, pid):
    bio = get_object_or_404(Bio, id=pid)
    return person_detail_abstract(request, bio)

def person_detail_abstract(request, bio):
    competition_stats = bio.competition_stats().order_by('competition__international', '-games_played')
    team_stats = bio.team_stats().order_by('-games_played')
    #league_stats = Stat.objects.filter(player=bio).filter(competition__ctype='League').order_by('season')
    league_stats = Stat.objects.filter(player=bio).order_by('season')
    domestic_stats = league_stats.filter(team__international=False)
    international_stats = league_stats.filter(team__international=True)
    
    context = {
        "bio": bio,
        'recent_game_stats': bio.gamestat_set.exclude(game__date=None).order_by('-game__date')[:10],
        'league_stats': league_stats,
        'domestic_stats': domestic_stats,
        'international_stats': international_stats,
        'competition_stats': competition_stats,
        'career_stat': bio.career_stat(),
        'game_log_count': bio.gamestat_set.count(),
        'team_stats': team_stats,
        'picks': bio.pick_set.exclude(draft__competition=None).order_by('draft__season', 'draft__start'),
        'coach_stats': bio.coachstat_set.order_by('season'),
        'positions': bio.position_set.order_by('start'),
        'refs': bio.ref_set()[:10]
        }

    return render(request, "bios/detail.html",
                              context)   


def random_person_detail(request):
    import random
    bios = Bio.objects.count()
    bio_id = random.randint(1, bios)
    bio_slug = Bio.objects.get(id=bio_id).slug
    return person_detail(request, bio_slug)




def person_detail_games(request, slug):
    bio = Bio.objects.by_slug(slug)
    career_stat = bio.career_stat()
    game_stats = bio.gamestat_set.order_by('game')
    
    if request.method == 'GET':
        form = BioGameStatForm(bio, request.GET)
        if form.is_valid():
            if form.cleaned_data['result']:
                game_stats = game_stats.filter(result=form.cleaned_data['result'])

            if form.cleaned_data['team']:
                game_stats = game_stats.filter(team=form.cleaned_data['team'])

            if form.cleaned_data['competition']:
                game_stats = game_stats.filter(game__competition=form.cleaned_data['competition'])

            if form.cleaned_data['starter']:
                game_stats = game_stats.filter(games_started=1)


    else:
        form = BioGameStatForm(bio)

    
    context = {
        'form': form,
        'bio': bio,
        'game_stats': game_stats,
        'game_log_count': bio.gamestat_set.count(),
        # Plenty of bios have no career stat line at all; the template treats
        # a missing total as "unknown" rather than zero.
        'career_games': career_stat.games_played if career_stat else None,
        'stat': AppearanceStat(bio, game_stats),
        }
    return render(request, "bios/detail_games.html",
                              context)




def person_detail_referee_games(request, slug):
    bio = Bio.objects.by_slug(slug)
    
    query = (Q(referee=bio) | Q(linesman1=bio) | Q(linesman1=bio) | Q(linesman1=bio))
    games = Game.objects.filter(query)
    form = BioGameStatForm(bio)

    context = {
        'form': form,
        'bio': bio,
        'games': games,
        }
    return render(request, "bios/referee.html",
                              context)   


def person_detail_goals(request, slug):
    bio = Bio.objects.by_slug(slug)

    context = {
        "goals": bio.goal_set.all(),
        }
    return render(request, "bios/detail_goals.html",
                              context)   


def person_detail_stats(request, slug):
    bio = Bio.objects.by_slug(slug)

    context = {
        'bio': bio,
        'stats': bio.stat_set.order_by('season'),
        }
    return render(request, "bios/detail_stats.html",
                              context)



