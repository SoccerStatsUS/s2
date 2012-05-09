from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from goals.models import Goal


def goals_index(request):
    # Turn this into a bunch of cool graphics?
    # Cache it?
    
    
    goal_minutes = sorted(Goal.objects.frequency().items())

    context = {
        'goal_count': Goal.objects.count(),
        'goal_minutes': goal_minutes,
        }
    return render_to_response("goals/index.html",
                              context,
                              context_instance=RequestContext(request))


