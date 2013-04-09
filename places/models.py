from django.contrib.gis.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify

from bios.models import Bio

"""
class Place(models.Model):
    country = models.ForeignKey(Country, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
"""    


class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name




class CountryManager(models.Manager):

    def find(self, s):

        try:
            return Country.objects.get(name=s)
        except:
            return Country.objects.create(name=s)


    def country_dict(self):
        """
        A dict mapping a team's name and short name to an id.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
        return d



class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #population = models.IntegerField(null=True)
    code = models.CharField(max_length=15)

    confederation = models.CharField(max_length=15)
    subconfederation = models.CharField(max_length=15)

    objects = CountryManager()

    def __unicode__(self):
        return self.name

    def games(self):
        from games.models import Game
        query = Q(city__country=self) | Q(country=self)
        return Game.objects.filter(query)

    class Meta:
        ordering = ('name',)



class StateManager(models.Manager):

    def find(self, state, country):
        try:
            return State.objects.get(name=state, country=country)
        except:
            return State.objects.create(name=state, country=country)


class State(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    abbreviation = models.CharField(max_length=5)
    country = models.ForeignKey(Country, null=True, blank=True)
    joined = models.DateField(null=True)

    objects = StateManager()

    def __unicode__(self):
        return self.name
        #return "%s, %s" % (self.name, self.country)

    class Meta:
        ordering = ('name',)



class StatePopulation(models.Model):

    state = models.ForeignKey(State)
    year = models.IntegerField()
    population = models.IntegerField(null=True)




class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    slug = models.SlugField(max_length=100)

    #geometry = models.PointField(srid=4326)


    def __unicode__(self):
        if self.state:
            return "%s, %s" % (self.name, self.state.abbreviation)
        elif self.country:
            return "%s, %s" % (self.name, self.country.name)
        else:
            return self.name

    class Meta:
        ordering = ('name',)




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
            slug = slugify(name)
            return Stadium.objects.create(name=name, slug=slug)




class Stadium(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False, max_length=100)
    
    short_name = models.CharField(max_length=255)

    address = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    city = models.ForeignKey(City, null=True, blank=True)
    #location = models.PointField()

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
    

    objects = StadiumManager()    

    def __unicode__(self):
        return self.name


    def open_string(self):
        if self.opened:
            return self.opened

        elif self.year_opened:
            return self.year_opened

        else:
            return None


    def goal_count(self):
        scores = self.game_set.values_list('team1_score', 'team2_score')
        game_score_totals = [sum([a or 0, b or 0]) for (a, b) in scores]
        return sum(game_score_totals)


    def close_string(self):
        if self.closed:
            return self.closed

        elif self.year_closed:
            return self.year_closed

        else:
            return None
            


    class Meta:
        ordering = ('name',)



    
