from django.db import models
from django.template.defaultfilters import slugify

from teams.models import Team
from bios.models import Bio
from competitions.models import Competition, Season

class DraftManager(models.Manager):

    def get_queryset(self):
        return super(DraftManager, self).get_queryset().filter(real=True)


class Draft(models.Model):

    competition = models.ForeignKey(Competition, null=True)
    season = models.ForeignKey(Season)
    #season = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)

    #objects = DraftManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Draft, self).save(*args, **kwargs)


    def __str__(self):
        return "%s %s %s" % (self.season, self.competition, self.name)

    class Meta:
        ordering = ('competition', 'season', 'start', 'name', )


class Pick(models.Model):
    draft = models.ForeignKey(Draft)
    number = models.IntegerField()

    team = models.ForeignKey(Team)
    former_team = models.ForeignKey(Team, null=True, related_name='former_team_set')

    text = models.CharField(max_length=255)
    player = models.ForeignKey(Bio, null=True)

    pick = models.ForeignKey('self', null=True, related_name='drafted_pick_set')

    position = models.CharField(max_length=5)


    def get_player(self):
        if self.player:
            return self.player
        else:
            if self.pick:
                return self.pick.get_player()
            else:
                return None


    def __str__(self):
        return "%s %s" % (self.number, self.player)

    class Meta:
        ordering = ('draft', 'number',)

