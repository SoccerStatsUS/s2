import datetime

from haystack.indexes import ModelSearchIndex
from haystack import site
from places.models import Stadium

class StadiumIndex(ModelSearchIndex):

    class Meta:
        fields = ['name', 'city']

site.register(Stadium, StadiumIndex)
    
