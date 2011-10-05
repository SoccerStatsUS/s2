from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.bios.models import Bio



def person_list_generic(request, person_list):
    context =  {
        "bios": person_list,
        }
    return render_to_response("bios/list.html",
                              context,
                              context_instance=RequestContext(request)
                              )    


def person_index(request):
    people = Bio.objects.all()
    return person_list_generic(request, people)


def person_detail(request, bio_id):
    bio = Bio.objects.get(id=bio_id)
    context = {
        "bio": bio
        }
    return render_to_response("bios/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   
