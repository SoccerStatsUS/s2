from django.db import models


from s2.teams.models import Team
from s2.bios.models import Bio

class Position(models.Model):
    # Something like Peter Wilt, Chicago Fire, 2010, 2011

    person = models.ForeignKey(Bio)
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=255)

    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s, %s, %s" % (self.person, self.team, self.name)


    class Meta:
        ordering = ('start', )
