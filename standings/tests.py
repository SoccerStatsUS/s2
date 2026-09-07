from types import SimpleNamespace

from django.template import Context, Template
from django.test import SimpleTestCase


class StandingsTableTests(SimpleTestCase):
    def test_accepts_annotated_standings_list(self):
        standing = SimpleNamespace(
            stage='',
            group='Western Conference',
            team=SimpleNamespace(name='FC Dallas', slug=''),
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

        html = template.render(Context({'standings': [standing]}))

        self.assertNotIn('Western Conference', html)
        self.assertEqual(html.count('<table class="standings">'), 1)
        self.assertIn('Dallas Burn', html)
