from django.db import models

class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            return Competition.objects.create(name=name)


class Competition(models.Model):
    name = models.CharField(max_length=255)

    objects = CompetitionManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class SeasonManager(models.Manager):

    def find(self, name, competition):
        try:
            return Season.objects.get(name=name, competition=competition)
        except:
            return Season.objects.create(name=name, competition=competition)


class Season(models.Model):
    name = models.CharField(max_length=255)
    competition = models.ForeignKey(Competition)

    objects = SeasonManager()

    def __unicode__(self):
        return "%s: %s" % (self.competition, self.name)

    class Meta:
        ordering = ("competition", "name")

