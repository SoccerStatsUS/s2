from types import SimpleNamespace
from unittest.mock import MagicMock

from django.template import Context, Template
from django.test import SimpleTestCase

from competitions.views import season_standings, stat_leaders


class QueryRows(list):
    def exists(self):
        return bool(self)

    def exclude(self, **kwargs):
        name, value = next(iter(kwargs.items()))
        return QueryRows(row for row in self if getattr(row, name) != value)


class SeasonStandingsTests(SimpleTestCase):
    def test_uses_most_common_historical_team_name(self):
        standing = SimpleNamespace(team_id=1, team=SimpleNamespace(name='FC Dallas'))
        season = MagicMock()
        season.standing_set.filter.return_value.select_related.return_value = [standing]
        season.game_set.values_list.return_value = [
            (1, 'Dallas Burn', 2, 'Columbus Crew'),
            (1, 'Dallas Burn', 3, 'D.C. United'),
        ]

        standings = season_standings(season)

        self.assertEqual(standings[0].team_display_name, 'Dallas Burn')

    def test_standings_template_groups_conferences_and_uses_historical_name(self):
        team = SimpleNamespace(name='FC Dallas', slug='')
        standing = SimpleNamespace(
            stage='',
            group='Western Conference',
            team=team,
            team_display_name='Dallas Burn',
            games=32,
            wins=12,
            shootout_wins=5,
            ties=None,
            shootout_losses=3,
            losses=12,
            points=41,
            goals_for=50,
            goals_against=48,
        )
        template = Template(
            "{% load standings %}{% standings_table standings 'competition,season' %}"
        )

        html = template.render(Context({'standings': QueryRows([standing])}))

        self.assertIn('Western Conference', html)
        self.assertIn('Dallas Burn', html)
        self.assertNotIn('FC Dallas', html)


class SeasonLeaderTests(SimpleTestCase):
    def test_stat_leaders_aggregates_player_totals(self):
        stats = MagicMock()

        stat_leaders(stats, 'goals')

        stats.filter.assert_called_once_with(goals__gt=0)
        values = stats.filter.return_value.values
        values.assert_called_once_with('player_id', 'player__name', 'player__slug')
        annotation = values.return_value.annotate.call_args.kwargs['value']
        self.assertEqual(annotation.source_expressions[0].name, 'goals')
        values.return_value.annotate.return_value.order_by.assert_called_once_with(
            '-value', 'player__name'
        )

    def test_leaders_template_renders_compact_categories(self):
        leader_groups = [
            {
                'label': 'Goals',
                'rows': [
                    {'player__name': 'Roy Lassiter', 'player__slug': '', 'value': 27}
                ],
            },
            {
                'label': 'Assists',
                'rows': [
                    {'player__name': 'Carlos Valderrama', 'player__slug': '', 'value': 17}
                ],
            },
        ]
        template = Template(
            '{% include "competitions/season/leaders.html" %}'
        )

        html = template.render(Context({'leader_groups': leader_groups}))

        self.assertIn('Goals', html)
        self.assertIn('Roy Lassiter', html)
        self.assertIn('<strong>27</strong>', html)
        self.assertIn('Assists', html)
        self.assertIn('Carlos Valderrama', html)
