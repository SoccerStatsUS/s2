import re
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class PlayerSummaryTests(SimpleTestCase):

    def test_leads_with_identity_and_recorded_career_totals(self):
        bio = SimpleNamespace(
            name='Roy Lassiter',
            height_display='5\'8"',
            weight_display='165 lbs',
            birthdate=None,
            birthplace=None,
            deathdate=None,
        )
        career_stat = SimpleNamespace(
            games_played=209,
            games_started=179,
            minutes=15858,
            goals=102,
            assists=38,
        )

        html = render_to_string('bios/helpers/summary.html', {
            'bio': bio,
            'career_stat': career_stat,
            'first_game': None,
            'last_game': None,
        })

        self.assertIn('<h1>Roy Lassiter</h1>', html)
        self.assertIn('<dd>209</dd>', html)
        self.assertIn('<dd>15,858</dd>', html)
        self.assertIn('<dd>102</dd>', html)
        self.assertNotIn('bio_image', html)


class StatRows(list):
    """As much queryset as stats_table asks for."""

    def exclude(self, **kwargs):
        return self

    def exists(self):
        return bool(self)


GAME_STAT = SimpleNamespace(
    game=SimpleNamespace(
        id=1,
        competition=SimpleNamespace(slug='major-league-soccer', abbreviation='MLS'),
        date=SimpleNamespace(year=1996, month=4, day=13),
        winner=None, stadium=None, city=None, country=None,
    ),
    team=SimpleNamespace(slug='dc-united'),
    opponent=SimpleNamespace(slug='san-jose-clash'),
    goals=1, assists=None, minutes=90,
)


class PlayerTabsTests(SimpleTestCase):
    """
    The tab strip sits above everything but the identity block, and the panes
    run summary (honors, career totals, the goal chart), then the season
    tables, then games.
    """

    bio = SimpleNamespace(
        name='Roy Lassiter', slug='roy-lassiter',
        height_display=None, weight_display=None,
        birthdate=None, birthplace=None, deathdate=None,
        salary_set=SimpleNamespace(exists=lambda: False),
        pick_set=SimpleNamespace(exists=lambda: False),
    )

    def render(self, **context):
        fields = dict(bio=self.bio, career_stat=None, first_game=None,
                      last_game=None, awards=[], honors=[], team_stats=[],
                      competition_stats=[], domestic_stats=[],
                      international_stats=[], show_goal_chart=False,
                      recent_game_stats=[], coach_stats=[], refs=[],
                      picks=self.bio.pick_set, game_log_count=0)
        fields.update(context)
        return render_to_string('bios/detail.html', fields)

    def panes(self, html):
        return re.findall(r'<div tab="([a-z]+)"', html)

    def test_panes_run_summary_stats_games(self):
        html = self.render(team_stats=StatRows([SimpleNamespace()]),
                           domestic_stats=StatRows([SimpleNamespace()]),
                           recent_game_stats=StatRows([GAME_STAT]))

        self.assertEqual(self.panes(html), ['summary', 'stats', 'games'])

    def test_tab_strip_precedes_every_pane(self):
        html = self.render(team_stats=StatRows([SimpleNamespace()]))

        self.assertLess(html.index('id="tab_block"'), html.index('<div tab='))

    def test_honors_ride_in_the_summary_pane(self):
        item = SimpleNamespace(season=None, year=1996,
                               award=SimpleNamespace(id=1, competition=None, name='MVP'))
        html = self.render(awards=[item],
                           honors=[{'award': item.award, 'label': 'MVP', 'items': [item]}])

        self.assertEqual(self.panes(html), ['summary'])
        self.assertLess(html.index('<div tab="summary"'), html.index('Honors'))

    def test_no_summary_pane_without_summary_content(self):
        html = self.render(domestic_stats=StatRows([SimpleNamespace()]))

        self.assertEqual(self.panes(html), ['stats'])


def award_item(award, season=None, year=None):
    return SimpleNamespace(award_id=id(award), award=award, season=season, year=year)


def season(name):
    return SimpleNamespace(name=name, slug=name,
                           competition=SimpleNamespace(slug='major-league-soccer'))


class GroupHonorsTests(SimpleTestCase):
    """
    The summary tab wants "Best XI (2003, 2008, ...)", not a row per season.
    """

    def test_one_entry_per_award_with_its_seasons(self):
        from bios.views import group_honors

        best_xi = SimpleNamespace(id=1, name='Best XI', competition=None)
        mvp = SimpleNamespace(id=2, name='MVP', competition=None)
        honors = group_honors([
            award_item(best_xi, season('2008')),
            award_item(mvp, season('2009')),
            award_item(best_xi, season('2003')),
            award_item(best_xi, season('2009')),
        ])

        assert [h['label'] for h in honors] == ['Best XI', 'MVP']
        assert [i.season.name for i in honors[0]['items']] == ['2003', '2008', '2009']

    def test_competition_named_only_when_the_award_name_repeats(self):
        from bios.views import group_honors

        misl = SimpleNamespace(slug='misl', abbreviation='MISL', name='MISL')
        nasl = SimpleNamespace(slug='nasl', abbreviation='NASL', name='NASL')
        honors = group_honors([
            award_item(SimpleNamespace(id=1, name='MVP', competition=misl), season('1979')),
            award_item(SimpleNamespace(id=2, name='MVP', competition=nasl), season('1984')),
            award_item(SimpleNamespace(id=3, name='Scoring Champion', competition=misl),
                       season('1980')),
        ])

        assert [h['label'] for h in honors] == ['MISL MVP', 'Scoring Champion', 'NASL MVP']

    def test_undated_awards_sort_last(self):
        from bios.views import group_honors

        hall = SimpleNamespace(id=1, name='Hall of Fame', competition=None)
        roy = SimpleNamespace(id=2, name='Rookie of the Year', competition=None)
        honors = group_honors([award_item(hall), award_item(roy, season('1968'))])

        assert [h['label'] for h in honors] == ['Rookie of the Year', 'Hall of Fame']
