from django.db import models
from django.template.defaultfilters import slugify

from teams.models import Team
from bios.models import Bio
from competitions.models import Competition, Season


class Currency(models.Model):
    name = models.CharField(max_length=255)


class ExchangeValue(models.Model):
    currency1 = models.ForeignKey(Currency)
    currency2 = models.ForeignKey(Currency)
    proportion = models.DecimalField()
    

class SalaryManager(models.Manager):

    def get_query_set(self):
        return super(DraftManager, self).get_query_set().filter(real=True)

class Salary(models.Model):

    person = models.ForeignKey(Bio)
    amount = models.DecimalField()

    season = models.ForeignKey(Season, null=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
