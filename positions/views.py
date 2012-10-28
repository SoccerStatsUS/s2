from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from bios.models import Bio
from positions.models import Position


def index(request):


    context = {
        'positions': Position.objects.all(),
        }

    return render_to_response("positions/index.html",
                              context,
                              context_instance=RequestContext(request)
                              )


def position_detail(request, slug):
    
    positions = Position.objects.filter(slug=slug)

    context = {
        'positions': positions.select_related(),
        }
    return render_to_response("positions/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )   



def manager_index(request):

    managers = Bio.objects.filter(position__name='Head Coach').distinct()
    positions = Position.objects.distinct_names()

    context = {
        'managers': managers,
        'positions': positions,
        }

    return render_to_response("positions/index.html",
                              context,
                              context_instance=RequestContext(request)
                              )
