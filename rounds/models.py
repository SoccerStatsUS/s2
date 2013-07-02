from django.contrib.gis.db import models


class Round(models.Model):
    """
    A round of a competition.
    """

    name = models.CharField(max_length=50)
    number = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField()

