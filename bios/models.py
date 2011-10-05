from django.db import models

class BioManager(models.Manager):

    def find(self, name):
        """
        Given a team name, determine the actual team.
        """

        try:
            bio = Bio.objects.get(name=name)
        except:
            print "Creating Bio for %s" % name
            bio = Bio.objects.create(name=name)

        return bio


class Bio(models.Model):
    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    height = models.IntegerField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    birthplace = models.CharField(max_length=250, null=True, blank=True)

    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    objects = BioManager()

    #source = models.CharField(max_length=500)

    class Meta:
        ordering = ('-birthdate',)
        
    def __unicode__(self):
        return self.name

        
        

