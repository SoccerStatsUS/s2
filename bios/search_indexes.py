import datetime

from haystack.indexes import ModelSearchIndex
from haystack import site

from bios.models import Bio

class BioIndex(ModelSearchIndex):

    class Meta:
        fields = ['name', 'birthplace']

site.register(Bio, BioIndex)
    
