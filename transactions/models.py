from django.db import models

from bios.models import Bio
from teams.models import Team



class TransactionManager(models.Manager):
    pass
            

class Transaction(models.Model):
    """
    Represents a transaction
    """

    ttype = models.CharField(max_length=100)

    date = models.DateField(null=True)

    person = models.ForeignKey(Bio, on_delete=models.CASCADE)
    
    team_from = models.ForeignKey(Team, related_name="transactions_from", null=True, on_delete=models.CASCADE)
    team_to = models.ForeignKey(Team, related_name="transactions_to", null=True, on_delete=models.CASCADE)


    objects = TransactionManager()    

