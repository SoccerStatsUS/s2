from django.db import models
from django.template.defaultfilters import slugify

from teams.models import Team
from bios.models import Bio
from competitions.models import Competition, Season


class Currency(models.Model):
    name = models.CharField(max_length=255)



class ExchangeValue(models.Model):
    from_currency = models.ForeignKey(Currency, related_name='from_rate')
    to_currency = models.ForeignKey(Currency, related_name='to_rate')
    proportion = models.FloatField()

    

class SalaryManager(models.Manager):

    def get_queryset(self):
        return super(DraftManager, self).get_queryset().filter(real=True)

class Salary(models.Model):

    person = models.ForeignKey(Bio)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)

    season = models.CharField(max_length=255)
    #start = models.DateField(blank=True, null=True)
    #end = models.DateField(blank=True, null=True)


    def __unicode__(self):
        return "%s: %s (%s)" % (self.person, self.amount, self.season)

    
    class Meta:
        ordering = ('season', )

