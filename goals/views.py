from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.goals.models import Goal


def goals_index(request):
    # Add a paginator.
    goals = Goal.objects.order_by("-date")[:50]
    context = {
        'goals': goals,
        }
    return render_to_response("goals/list.html",
                              context,
                              context_instance=RequestContext(request))


