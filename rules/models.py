from django.db import models



class Rule(models.Model):
    description = models.CharField(max_length=255)    

    
class RuleSet(models.Model):
    name = models.CharField(max_length=255)    
    rules = models.ManyToManyField(Rule)  #, through='RuleBinding'




