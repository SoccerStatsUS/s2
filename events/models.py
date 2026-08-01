from django.db import models

from bios.models import Bio
from games.models import Game


class Event(models.Model):

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    minute = models.IntegerField(null=True)    

    description = models.CharField(max_length=255)


class Foul(models.Model):

    subject = models.ForeignKey(Bio, related_name="fouls_committed", on_delete=models.CASCADE)
    object = models.ForeignKey(Bio, null=True, related_name="fouls_suffered", on_delete=models.CASCADE)
    
    red = models.BooleanField()
    yellow = models.BooleanField()
    minute = models.IntegerField(null=True)

    description = models.CharField(max_length=255)


