from types import SimpleNamespace
from unittest.mock import MagicMock

from django.template import Context, Template
from django.test import SimpleTestCase

from competitions.views import season_standings


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
