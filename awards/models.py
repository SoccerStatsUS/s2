from django.db import models

from s2.bios.models import Bio

class Award(models.Model):
    
    name = models.CharField(max_length=255)


class AwardItem(models.Model):
    
    player = models.ForeignKey(Bio)
    position = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    votes = models.IntegerField(null=True)
    
    

