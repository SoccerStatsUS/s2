from collections import Counter, defaultdict
import json

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from goals.models import Goal
from lineups.models import Appearance
from stats.models import CompetitionStat



def graphs_index(request):
    context = {}
    return render_to_response("graphs/index.html",
                              context,
                              context_instance=RequestContext(request))




def map_graph(request):
    context = {}
    return render_to_response("graphs/map.html",
                              context,
                              context_instance=RequestContext(request))



def month_distribution(stat_qs):
    d = defaultdict(int)
    for birthdate, minutes in stat_qs.values_list('player__birthdate', 'minutes'):
        #d[birthdate.month] += minutes
        d[birthdate.month] += 1
    return sorted(d.items())
    



def age_bias_graph(request):

    stats = CompetitionStat.objects.filter(competition__slug='major-league-soccer').exclude(player__birthplace__country=None).exclude(player__birthdate=None)

    domestic_dist = month_distribution(stats.filter(player__birthplace__country__slug='united-states'))
    international_dist = month_distribution(stats.exclude(player__birthplace__country__slug='united-states'))


    context = {
        'domestic_distribution': json.dumps(domestic_dist),
        'international_distribution': json.dumps(international_dist),
        }
    return render_to_response("graphs/bias.html",
                              context,
                              context_instance=RequestContext(request))

    

