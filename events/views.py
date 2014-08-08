from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from events.models import Event, Foul


def events_index(request):
    
    #goal_minutes = sorted(Goal.objects.frequency().items())

    context = {
        'goal_count': Goal.objects.count(),
        'goal_minutes': goal_minutes,
        }
    return render_to_response("goals/index.html",
                              context,
                              context_instance=RequestContext(request))


