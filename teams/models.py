from django.db import models
from django.template.defaultfilters import slugify

class DefunctTeamManager(models.Manager):
    def get_query_set(self):
        return super(DefunctTeamManager, self).get_query_set().filter(defunct=True, real=True)

class RealTeamManager(models.Manager):
    def get_query_set(self):
        return super(RealTeamManager, self).get_query_set().filter(real=True)

class TeamManager(models.Manager):

    def find(self, name):
        """
        Given a team name, determine the actual team.
        """
        #from soccer.teams.aliases import mapping
        teams = Team.objects.filter(name=name)
        if teams:
            return teams[0]

        teams = Team.objects.filter(short_name=name)
        if teams:
            return teams[0]

        team = Team.objects.create(
            name=name, 
            short_name=name, 
            slug=slugify(name))
        return team


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # Let's get rid of short name! It's really just another alias.
    # No way, it's useful when you want to display a better name.
    # Let's just be clear that it's very optional.
    short_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    founded = models.IntegerField(null=True, blank=True)

    # Have some virtual teams from USMNT drafts.
    real = models.BooleanField(default=True)
    defunct = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    objects = TeamManager()
    defuncts = DefunctTeamManager()
    reals = RealTeamManager()

    class Meta:
        ordering = ('short_name',)

    def fancy_name(self):
        return self.name

    @property
    def normal_name(self):
        if self.short_name:
            return self.short_name
        return self.name

    def __unicode__(self):
        return self.short_name


