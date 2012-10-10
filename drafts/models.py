from django.db import models
from django.template.defaultfilters import slugify

from teams.models import Team
from bios.models import Bio
from competitions.models import Competition, Season

class DraftManager(models.Manager):

    def get_query_set(self):
        return super(DraftManager, self).get_query_set().filter(real=True)


class Draft(models.Model):

    competition = models.ForeignKey(Competition)

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    season = models.CharField(max_length=255)
    
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)

    #objects = DraftManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Draft, self).save(*args, **kwargs)


    def __unicode__(self):
        return "%s %s" % (self.competition, self.name)

    class Meta:
        ordering = ('competition', 'season', 'start', 'name', )


class Pick(models.Model):
    draft = models.ForeignKey(Draft)
    number = models.IntegerField()

    team = models.ForeignKey(Team)
    former_team = models.ForeignKey(Team, null=True, related_name='former_team_set')

    text = models.CharField(max_length=255)
    player = models.ForeignKey(Bio, null=True)

    position = models.CharField(max_length=5)




    def __unicode__(self):
        return "%s %s" % (self.number, self.player)

    class Meta:
        ordering = ('draft', 'number',)

