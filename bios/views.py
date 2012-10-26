from collections import OrderedDict, Counter

from django.db.models import Sum
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from stats.models import Stat

from bios.forms import BioAppearanceForm

def person_list_generic(request, person_list=None):

    if person_list is None:
        stats = Stat.career_stats.all()[:1000]
    else:
        stats = Stat.career_stats.filter(player__in=person_list)

    context =  {
        'stats': stats,
        }
    return render_to_response("bios/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )    

class AppearanceStanding(object):
    # Use this to generate a standing for a given set of appearances.
    def __init__(self, appearances):
        self.appearances = appearances
        self.goals_for = appearances.exclude(goals_for=None).aggregate(Sum('goals_for'))['goals_for__sum']
        self.goals_against = appearances.exclude(goals_against=None).aggregate(Sum('goals_for'))['goals_against__sum']
        results = [e[0] for e in appearances.filter(result__in='wlt').values_list('result')]
        c = Counter(results)
        self.wins, self.ties, self.losses = c['w'], c['t'], c['l']
        


def one_word(request):
    bios = Bio.objects.exclude(name__contains=' ')
    return person_list_generic(request, bios)
    


@cache_page(60 * 60 * 12)
def person_index(request):

    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    name_dict = OrderedDict()

    for letter in letters:
        stats = Stat.career_stats.filter(player__name__istartswith=letter).order_by('-player__hall_of_fame', '-games_played')[:5]
        name_dict[letter] = stats

    context = {
        'name_dict': name_dict
        }

    return render_to_response("bios/index.html",
                              context,
                              context_instance=RequestContext(request))



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
    
    context = {
        "bio": bio,
        'recent_appearances': bio.appearance_set.all()[:10],
        }
    return render_to_response("bios/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   


def person_detail_games(request, slug):
    bio = get_object_or_404(Bio, slug=slug)
    
    if request.method == 'POST':
        form = BioAppearanceForm(bio, request.POST)
        if form.is_valid():
            if form.cleaned_data['result']:
                games = games.filter(result=form.cleaned_data['result'])

            if form.cleaned_data['team']:
                games = games.filter(team=form.cleaned_data['team'])

            if form.cleaned_data['competition']:
                games = games.filter(game__competition=form.cleaned_data['competition'])

    else:
        form = BioAppearanceForm(bio, request.POST)
    
    context = {
        'form': form,
        'appearances': bio.appearance_set.all(),
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




@cache_page(60 * 24)
def bio_detail_stats(request):

    player_id = request.GET.get('playerid')
    
    bio = Bio.objects.get(id=player_id)

    competition_stats = bio.competition_stats()
    domestic_competition_stats = competition_stats.filter(competition__international=False).order_by('-games_played')

    league_stats = Stat.objects.filter(player__id=player_id).filter(competition__ctype='League').order_by('season')

    
    context = {
        'league_stats': league_stats,
        'domestic_competition_stats': domestic_competition_stats,
        'career_stats': bio.career_stats(),
        }

    return render_to_response("bios/detail_stats.html",
                              context,
                              context_instance=RequestContext(request))

