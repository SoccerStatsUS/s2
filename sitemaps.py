from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from awards.models import Award
from bios.models import Bio
from competitions.models import Competition, Season
from games.models import Game
from organizations.models import Confederation
from places.models import City, Country, Stadium, State
from sources.models import Source
from teams.models import Team


class StaticSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'

    def items(self):
        return ['home', 'everything_index', 'about_index',
                'competition_index', 'team_index',
                'person_index', 'dates_index', 'award_index', 'drafts_index',
                'team_standings', 'seasons_dashboard',
                'games_index', 'goals_index', 'lineup_index',
                'standings_index', 'stats_index',
                'places_index', 'country_index', 'state_index', 'city_index',
                'stadium_index', 'organizations_index',
                'source_index', 'manager_index']

    def location(self, item):
        return reverse(item)


class CompetitionSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Competition.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('competition_detail', args=[obj.slug])


class SeasonSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Season.objects.exclude(slug='').exclude(competition__slug='') \
            .select_related('competition').order_by('id')

    def location(self, obj):
        return reverse('season_detail', args=[obj.competition.slug, obj.slug])


class TeamSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Team.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('team_detail', args=[obj.slug])


class BioSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Bio.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('person_detail', args=[obj.slug])


class YearSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        years = Game.objects.exclude(date=None).dates('date', 'year')
        return [d.year for d in years]

    def location(self, year):
        return reverse('year_detail', args=[year])


class StadiumSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Stadium.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('stadium_detail', args=[obj.slug])


class CitySitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return City.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('city_detail', args=[obj.slug])


class StateSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return State.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('state_detail', args=[obj.slug])


class CountrySitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Country.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('country_detail', args=[obj.slug])


class ConfederationSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Confederation.objects.exclude(slug='').order_by('id')

    def location(self, obj):
        return reverse('confederation_detail', args=[obj.slug])


class AwardSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Award.objects.order_by('id')

    def location(self, obj):
        return reverse('award_detail', args=[obj.id])


class SourceSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Source.objects.order_by('id')

    def location(self, obj):
        return reverse('source_detail', args=[obj.id])


SITEMAPS = {
    'static': StaticSitemap,
    'competitions': CompetitionSitemap,
    'seasons': SeasonSitemap,
    'teams': TeamSitemap,
    'players': BioSitemap,
    # No games section: /games/<id>/ is keyed on the auto pk, which is
    # reassigned every rebuild, so those URLs cannot be submitted as stable.
    'years': YearSitemap,
    'stadiums': StadiumSitemap,
    'cities': CitySitemap,
    'states': StateSitemap,
    'countries': CountrySitemap,
    'confederations': ConfederationSitemap,
    'awards': AwardSitemap,
    'sources': SourceSitemap,
}
