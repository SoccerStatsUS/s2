from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from organizations.models import Confederation
from places.models import Country, game_stats_by_country


@cache_page(60 * 60 * 12)
def organizations_index(request):

    stats = game_stats_by_country()
    country_to_confederation = dict(Country.objects.values_list('id', 'confederation_id'))

    confederations = list(Confederation.objects.annotate(member_count=Count('country')))
    for confederation in confederations:
        confederation.game_count = sum(
            row['games'] for cid, row in stats.items()
            if country_to_confederation.get(cid) == confederation.id)
    confederations.sort(key=lambda c: -c.game_count)

    context = {
        'confederations': confederations,
        }

    return render(request, "organizations/index.html",
                              context)


@cache_page(60 * 60 * 12)
def confederation_detail(request, confederation_slug):
    confederation = get_object_or_404(Confederation, slug=confederation_slug)

    stats = game_stats_by_country()
    countries = list(confederation.country_set.all())
    for country in countries:
        row = stats.get(country.id)
        country.game_count = row['games'] if row else 0
        country.total_attendance = row['attendance'] if row else None
    countries.sort(key=lambda c: (-c.game_count, c.name))

    context = {
        'confederation': confederation,
        'countries': countries,
        'show_subconfederation': any(c.subconfederation for c in countries),
        }

    return render(request, "organizations/confederation/detail.html",
                              context)
