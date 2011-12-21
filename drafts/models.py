from django.db import models
from django.template.defaultfilters import slugify

from s2.teams.models import Team
from s2.bios.models import Bio
from s2.competitions.models import Competition, Season

class Draft(models.Model):

    competition = models.ForeignKey(Competition, null=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    #date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Draft, self).save(*args, **kwargs)


    def __unicode__(self):
        return "%s %s" % (self.competition, self.name)

    class Meta:
        ordering = ('competition', 'name', )


class Pick(models.Model):
    draft = models.ForeignKey(Draft)

    text = models.CharField(max_length=255)
    player = models.ForeignKey(Bio, null=True)
    position = models.IntegerField()
    team = models.ForeignKey(Team)

