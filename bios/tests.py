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
