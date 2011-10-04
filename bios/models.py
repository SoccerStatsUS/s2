from django.db import models

class Bio(models.Model):
    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    height = models.IntegerField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    birthplace = models.CharField(max_length=250, null=True, blank=True)

    #source = models.CharField(max_length=500)

    class Meta:
        ordering = ('-birthdate',)
        
    def __unicode__(self):
        return self.name

        
        

