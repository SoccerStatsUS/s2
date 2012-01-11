import datetime

from haystack.indexes import ModelSearchIndex
from haystack import site
from s2.teams.models import Team

class TeamIndex(ModelSearchIndex):

    class Meta:
        fields = ['name', 'short_name', 'founded']

site.register(Team, TeamIndex)
    
