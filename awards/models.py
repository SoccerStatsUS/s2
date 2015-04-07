from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from competitions.models import Competition, Season

class Award(models.Model):
    
    name = models.CharField(max_length=255)
    competition = models.ForeignKey(Competition, null=True)
    #date = models.DateField()

    # This is used to distinguish awards that are named differently but mean the same thing.
    # e.g. MVP, Golden ? (whatever the best World Cup player wins.)
    # Golden boot / top scorer.
    # Supporters Shield, Champion, etc.
    type = models.CharField(max_length=255)


    def is_multi(self):
        """
        Award has multiple winners in a single season, e.g. Best XI
        """
        s = set()
        for e in self.awarditem_set.all():
            season = e.season
            if season in s:
                return True
            s.add(season)
        return False


    def __unicode__(self):
        if self.competition:
            return "%s %s" % (self.competition.name, self.name)
        else:
            return "No Competition %s" % self.name

    class Meta:
        ordering = ('competition', 'name')


class AwardItem(models.Model):
    """
    An individual award, like the 1998 MLS MVP.
    Can be applied either to a season or a year.
    """

    award = models.ForeignKey(Award)
    season = models.ForeignKey(Season, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    #content_type = models.ForeignKey(ContentType)


    object_id = models.PositiveIntegerField()
    #recipient = generic.GenericForeignKey()

    #def __unicode__(self):
    #    return "%s %s %s" % (self.season, self.award.name, self.recipient)

    class Meta:
        ordering = ("year", 'season')
