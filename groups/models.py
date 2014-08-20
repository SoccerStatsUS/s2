from django..db import models


class Group(models.Model):
    """
    A group of a competition.
    """
    # Western conference?
    # Group A, World Cup
    # Zones?

    name = models.CharField(max_length=50)
    # region?
    # 


