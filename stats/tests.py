from django.test import TestCase

from bios.models import Bio
from competitions.models import Competition, Season, SuperSeason
from stats.models import Stat
from teams.models import Team


class StatsIndexFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mls = Competition.objects.create(name='Major League Soccer')
        nwsl = Competition.objects.create(name="National Women's Soccer League")
        ss = SuperSeason.objects.create(name='2019', order=1, order2=1)
        mls19 = Season.objects.create(name='2019', competition=mls, super_season=ss)
        nwsl19 = Season.objects.create(name='2019', competition=nwsl, super_season=ss)
        ss20 = SuperSeason.objects.create(name='2020', order=2, order2=2)
        mls20 = Season.objects.create(name='2020', competition=mls, super_season=ss20)
        galaxy = Team.objects.create(name='LA Galaxy', short_name='LA Galaxy')
        fire = Team.objects.create(name='Chicago Fire', short_name='Chicago Fire')
        thorns = Team.objects.create(name='Portland Thorns', short_name='Portland Thorns')
        a, b, c = (Bio.objects.create(name=n, hall_of_fame=False) for n in ('Ann Able', 'Bob Baker', 'Cy Cole'))
        Stat.objects.create(player=a, competition=mls, season=mls19, team=galaxy, games_played=30)
        Stat.objects.create(player=b, competition=mls, season=mls19, team=fire, games_played=20)
        Stat.objects.create(player=b, competition=mls, season=mls20, team=fire, games_played=10)
        Stat.objects.create(player=c, competition=nwsl, season=nwsl19, team=thorns, games_played=5)

    def get(self, **params):
        return self.client.get('/stats/', params, HTTP_HOST='localhost')

    def test_unfiltered_lists_everything(self):
        r = self.get()
        assert r.status_code == 200
        assert r.context['page'].paginator.count == 4
        assert not r.context['filtered']

    def test_each_filter_narrows(self):
        assert self.get(competition='major-league-soccer').context['page'].paginator.count == 3
        assert self.get(season='2019').context['page'].paginator.count == 3
        assert self.get(team='chicago-fire').context['page'].paginator.count == 2

    def test_filters_compose(self):
        r = self.get(competition='major-league-soccer', season='2019', team='chicago-fire')
        assert [s.player.name for s in r.context['stats']] == ['Bob Baker']

    def test_choices_follow_the_other_filters(self):
        r = self.get(competition='national-womens-soccer-league')
        assert [t.name for t in r.context['teams']] == ['Portland Thorns']
        assert list(r.context['seasons']) == ['2019']
        # The competition list is never narrowed by itself.
        assert [c.name for c in r.context['competitions']] == ['Major League Soccer', "National Women's Soccer League"]

    def test_an_unknown_slug_matches_nothing(self):
        r = self.get(team='no-such-team')
        assert r.status_code == 200
        assert r.context['page'].paginator.count == 0
        assert b'No stat lines match' in r.content
