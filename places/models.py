from django.db import models
from django.template.defaultfilters import slugify

class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)

class State(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)


class Place(models.Model):
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)

    state = models.ForeignKey(State, null=True, blank=True)
    country = models.ForeignKey(Country)

    #location = models.PointField()
