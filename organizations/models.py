from django.db import models

from django.template.defaultfilters import slugify

from bios.models import Bio

class Confederation(models.Model):
    """
    A confederation
    """

    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)

    slug = models.SlugField(max_length=150)

    region = models.CharField(max_length=255)

    founded = models.DateField(null=True)

#class Organization(models.Model):
#    #eg USSF, ...
#    pass


