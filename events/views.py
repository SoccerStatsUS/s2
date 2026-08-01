from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from events.models import Event, Foul


def events_index(request):
    
    #goal_minutes = sorted(Goal.objects.frequency().items())

    context = {
        'goal_count': Goal.objects.count(),
        'goal_minutes': goal_minutes,
        }
    return render(request, "goals/index.html",
                              context)


