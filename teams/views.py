from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from s2.teams.models import Team

def team_detail(request, team_id):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, id=team_id)

    context = {
        'team': team,
        }

    return render_to_response("teams/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    

