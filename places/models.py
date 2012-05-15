from django.db import models
from django.template.defaultfilters import slugify

from bios.models import Bio


class CountryManager(models.Manager):

    def find(self, s):

        try:
            return Country.objects.get(name=s)
        except:
            return Country.objects.create(name=s)


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)

    objects = CountryManager()

    def __unicode__(self):
        return self.name

class StateManager(models.Manager):

    def find(self, state, country):
        try:
            return State.objects.get(name=state, country=country)
        except:
            return State.objects.create(name=state, country=country)


        

class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, null=True, blank=True)

    objects = StateManager()

    def __unicode__(self):
        return "%s, %s" % (self.name, self.country)


class CityManager(models.Manager):

    def find(self, d):
        """
        Given a city dict, get the City object.
        """

        country = Country.objects.find(d['country'])

        if d['state']:
            state = State.objects.find(d['state'], country)
        else:
            state = None
        
        cities = City.objects.filter(name=d['city'], state=state, country=country)

        if len(cities) == 0:
            return City.objects.create(name=d['city'], state=state, country=country)
        elif len(cities) == 1:
            return cities[0]
        else:
            import pdb; pdb.set_trace()
            x = 5
        

class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)

    objects = CityManager()

    def __unicode_(self):
        if self.state:
            return "%s, %s" % (self.name, self.state.name)
        else:
            return "%s, %s" % (self.name, self.country.name)



class StadiumManager(models.Manager):

    def as_dict(self):
        """
        Dict mapping names to stadium id's.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d


    def find(self, name, create=True):
        """
        Given a team name, determine the actual team.
        """
        # Not here?
        if name == '':
            import pdb; pdb.set_trace()
        
        stadiums = Stadium.objects.filter(name=name)
        if stadiums:
            return stadiums[0]
        else:
            return Stadium.objects.create(name=name)




class Stadium(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)
    
    short_name = models.CharField(max_length=255)

    #city = models.ForeignKey(City, null=True, blank=True)

    address = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    opened = models.DateField(null=True)
    year_opened = models.IntegerField(null=True)

    closed = models.DateField(null=True)
    year_closed = models.IntegerField(null=True)
    
    architect = models.ForeignKey(Bio, null=True)

    capacity = models.IntegerField(null=True)

    width = models.CharField(max_length=255)
    length = models.CharField(max_length=255)
    measure = models.CharField(max_length=255)

    cost = models.DecimalField(max_digits=31, decimal_places=2, null=True)
    denomination = models.CharField(max_length=255)

    notes = models.CharField(max_length=255)
    
    #location = models.PointField()
    objects = StadiumManager()    

    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ('name',)
