from django.db import models
from django.template.defaultfilters import slugify


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, null=True, blank=True)


class Stadium(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, null=True, blank=True)
    
    
    #location = models.PointField()
