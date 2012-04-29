from collections import OrderedDict

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from stats.models import Stat

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



def one_word(request):
    bios = Bio.objects.exclude(name__contains=' ')
    return person_list_generic(request, bios)
    


@cache_page(60 * 60 * 12)
def person_index(request):
    # Change this to something like: http://www.baseball-reference.com/players/

    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    name_dict = OrderedDict()

    for letter in letters:
        stats = Stat.career_stats.filter(player__name__istartswith=letter)[:5]
        name_dict[letter] = stats

    context = {
        'name_dict': name_dict
        }

    return render_to_response("bios/index.html",
                              context,
                              context_instance=RequestContext(request))



def name_fragment(request, fragment):
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
    
    # Should not be doing this here.
    bio.calculate_standings()
    
    context = {
        "bio": bio
        }
    return render_to_response("bios/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   
