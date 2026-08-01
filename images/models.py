from collections import defaultdict
import datetime
import os

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse



class Image(models.Model):

    filename = models.CharField(max_length=200, unique=True)

    # Affiliate team. e.g.
    # Portland Timbers Reserves -> Portland Timbers (reserve -> main)
    # Chicago Fire Select -> Chicago Fire (? affiliation)
    # United States -> United States U-20 (youth team)
    #affiliate = models.ForeignKey('self', null=True)

    #src = models.ImageField('self', null=True)

    #content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    #target = GenericForeignKey('content_type', 'object_id')


    def path(self):
        return "/static/images/bios/mls/" + self.filename



