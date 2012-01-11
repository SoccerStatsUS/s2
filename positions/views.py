from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.bios.models import Bio
from s2.positions.models import Position


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
