from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from goals.models import Goal


def goals_index(request):
    # Turn this into a bunch of cool graphics?
    # Cache it?
    
    
    goal_minutes = sorted((k, v) for k, v in Goal.objects.frequency().items() if k is not None)

    context = {
        'goal_count': Goal.objects.count(),
        'goal_minutes': goal_minutes,
        }
    return render(None, "goals/index.html",
                              context)


