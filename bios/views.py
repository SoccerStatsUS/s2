from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.bios.models import Bio
from s2.stats.models import Stat



def person_list_generic(request, person_list):
    context =  {
        "bios": person_list,
        "stats": Stat.career_stats.all()
        }
    return render_to_response("bios/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )    


def person_index(request):
    people = Bio.objects.all()
    return person_list_generic(request, people)


def bad_bios(request):
    
    context = {
        'duplicate_slugs': Bio.objects.duplicate_slugs(),
        }

    return render_to_response("bios/bad.html",
                              context,
                              context_instance=RequestContext(request)
                              )    
                              


def person_detail(request, slug):
    bio = Bio.objects.get(slug=slug)
    context = {
        "bio": bio
        }
    return render_to_response("bios/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   
