from collections import OrderedDict, Counter

from django.db.models import Sum
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from stats.models import Stat, CareerStat

from bios.forms import BioAppearanceForm



class AppearanceStat(object):
    def __init__(self, player, appearances):
        from goals.models import Goal, Assist

        self.player = player

        self.goals_for = appearances.exclude(goals_for=None).aggregate(Sum('goals_for'))['goals_for__sum']
        self.goals_against = appearances.exclude(goals_against=None).aggregate(Sum('goals_against'))['goals_against__sum']
        results = [e[0] for e in appearances.filter(result__in='wlt').values_list('result')]
        c = Counter(results)
        self.wins, self.ties, self.losses = c['w'], c['t'], c['l']
        self.games = appearances.count()

        if self.games:
            self.win_percentage_100 =  (self.wins + .5 * self.ties) / self.games
        else:
            self.win_percentage_100 = 0

        game_ids = appearances.values_list('game')

        self.games_played = len(game_ids)
        self.games_started = appearances.filter(on=0).count()

        self.minutes = appearances.exclude(minutes=None).aggregate(Sum('minutes'))['minutes__sum']
        self.goals = Goal.objects.filter(player=self.player, game__id__in=game_ids).count()
        self.assists = Assist.objects.filter(player=self.player, goal__game__id__in=game_ids).count()




def person_list_generic(request, person_list=None):

    if person_list is None:
        stats = CareerStat.objects.all()[:1000]
    else:
        stats = CareerStat.objects.filter(player__in=person_list)

    context =  {
        'stats': stats.select_related(),
        }
    return render_to_response("bios/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )    

        

def one_word(request):
    bios = Bio.objects.exclude(name__contains=' ')
    return person_list_generic(request, bios)
    


@cache_page(60 * 60 * 12)
def person_index(request):

    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()
    stats = CareerStat.objects.order_by('-player__hall_of_fame', '-games_played').select_related()

    name_dict = OrderedDict()
    for letter in letters:
        name_dict[letter] = stats.filter(player__name__istartswith=letter)[:5]

    context = {
        'name_dict': name_dict
        }

    return render_to_response("bios/index.html",
                              context,
                              context_instance=RequestContext(request))


@cache_page(60 * 60 * 12)
def bio_name_fragment(request, fragment):
    return person_list_generic(request,
                               Bio.objects.filter(name__istartswith=fragment))


def bad_bios(request):

    context = {
        'duplicate_slugs': Bio.objects.duplicate_slugs(),
        }

    return render_to_response("bios/bad.html",
                              context,
                              context_instance=RequestContext(request)
                              )    
                              


def person_detail(request, slug):
    bio = get_object_or_404(Bio, slug=slug)
    
    competition_stats = bio.competition_stats().order_by('-games_played')
    team_stats = bio.team_stats().order_by('-games_played')
    league_stats = Stat.objects.filter(player=bio).filter(competition__ctype='League').order_by('season')
    
    context = {
        "bio": bio,
        'recent_appearances': bio.appearance_set.all()[:10],

        'league_stats': league_stats,
        'competition_stats': competition_stats,
        'career_stats': bio.career_stats(),
        'team_stats': team_stats,
        }


    return render_to_response("bios/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   


def person_detail_games(request, slug):
    bio = get_object_or_404(Bio, slug=slug)
    appearances = bio.appearance_set.all()
    
    if request.method == 'GET':
        form = BioAppearanceForm(bio, request.GET)
        if form.is_valid():
            if form.cleaned_data['result']:
                appearances = appearances.filter(result=form.cleaned_data['result'])

            if form.cleaned_data['team']:
                appearances = appearances.filter(team=form.cleaned_data['team'])

            if form.cleaned_data['competition']:
                appearances = appearances.filter(game__competition=form.cleaned_data['competition'])

            if form.cleaned_data['starter']:
                appearances = appearances.filter(on=0)


    else:
        form = BioAppearanceForm(bio)

    
    context = {
        'form': form,
        'appearances': appearances,
        'stat': AppearanceStat(bio, appearances),
        }
    return render_to_response("bios/detail_games.html",
                              context,
                              context_instance=RequestContext(request)
                              )   

def person_detail_goals(request, slug):
    bio = get_object_or_404(Bio, slug=slug)

    context = {
        "goals": bio.goal_set.all(),
        }
    return render_to_response("bios/detail_goals.html",
                              context,
                              context_instance=RequestContext(request)
                              )   


def person_detail_stats(request, slug):
    bio = get_object_or_404(Bio, slug=slug)

    context = {
        "stats": bio.goal_set.all(),
        }
    return render_to_response("bios/detail_stats.html",
                              context,
                              context_instance=RequestContext(request)
                              )   



