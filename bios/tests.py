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
                      last_game=None, awards=[], team_stats=[],
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
        html = self.render(awards=[SimpleNamespace(season=None, year=1996,
                                                   award=SimpleNamespace(id=1, competition=None,
                                                                         name='MVP'))])

        self.assertEqual(self.panes(html), ['summary'])
        self.assertLess(html.index('<div tab="summary"'), html.index('Honors'))

    def test_no_summary_pane_without_summary_content(self):
        html = self.render(domestic_stats=StatRows([SimpleNamespace()]))

        self.assertEqual(self.panes(html), ['stats'])
