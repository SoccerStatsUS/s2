import datetime

from haystack.indexes import *
from haystack import site
from s2.bios.models import Bio

class BioIndex(SearchIndex):
    text = CharField(document=True)
    birthplace = CharField(model_attr='birthplace')
    
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        #return Note.objects.filter(pub_date__lte=datetime.datetime.now())
        return Bio.objects.all()

site.register(Bio, BioIndex)
    
