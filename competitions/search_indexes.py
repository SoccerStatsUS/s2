import datetime

from haystack.indexes import ModelSearchIndex
from haystack import site
from competitions.models import Competition

class CompetitionIndex(ModelSearchIndex):

    class Meta:
        fields = ['name']

site.register(Competition, CompetitionIndex)
