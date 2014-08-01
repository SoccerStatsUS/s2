from django.db import models

from django.template.defaultfilters import slugify

from bios.models import Bio

class Confederation(models.Model):
    name = models.CharField(max_length=255)


#class Organization(models.Model):
#    #eg USSF, ...
#    pass


