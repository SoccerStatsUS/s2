from django.db import models


from s2.teams.models import Team
from s2.bios.models import Person

class Position(models.Model):
    # Something like Peter Wilt, Chicago Fire, 2010, 2011

    person = models.ForeignKey(Person)    
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=255)

    start = models.DateField()
    end = models.DateField(null=True, blank=True)
