



class Event(models.Model):

    game = models.ForeignKey(Game, null=True)
    minute = models.IntegerField(null=True)    

    description = models.CharField(max_length=255)


class Foul(models.Model):

    subject = models.ForeignKey(Player)
    object = models.ForeignKey(Player, null=True)
    
    red = models.BooleanField()
    yellow = models.BooleanField()
    minute = models.IntegerField(null=True)

    description = models.CharField(max_length=255)


