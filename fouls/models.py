





class Foul(models.Model):

    player = models.ForeignKey(Player)
    
    red = models.BooleanField()
    yellow = models.BooleanField()
    minute = models.IntegerField(null=True)

    description = models.CharField(max_length=255)

