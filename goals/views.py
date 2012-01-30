from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from goals.models import Goal
from goals.forms import GoalForm


def goals_index(request):
    goals = Goal.objects.order_by("-date")[:50]
    context = {
        'goals': goals,
        'form': GoalForm(),
        }
    return render_to_response("goals/list.html",
                              context,
                              context_instance=RequestContext(request))


