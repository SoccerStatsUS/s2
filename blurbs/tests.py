from types import SimpleNamespace
from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase

from blurbs.loading import get_blurb_target
from blurbs.models import Blurb
from competitions.models import Competition, Season, SuperSeason
from teams.models import Team


class BlurbTests(SimpleTestCase):
    def test_competitions_seasons_and_teams_expose_blurbs(self):
        for model in (Competition, Season, Team):
            relation = model._meta.get_field("blurbs")
            self.assertIs(relation.remote_field.model, Blurb)

    def test_renders_as_prose(self):
        html = render_to_string(
            "blurbs/list.html",
            {"blurbs": [SimpleNamespace(text="A short piece of history.")]},
        )

        self.assertEqual(html, '<p class="blurb">A short piece of history.</p>\n')

    @patch("blurbs.loading.Team")
    @patch("blurbs.loading.Season")
    @patch("blurbs.loading.Competition")
    def test_resolves_each_supported_target(self, competition, season, team):
        competition_target = get_blurb_target(
            {"kind": "competition", "competition": "Major League Soccer"}
        )
        season_target = get_blurb_target(
            {
                "kind": "season",
                "competition": "American Soccer League (1921-1933)",
                "season": "1928-1929",
            }
        )
        team_target = get_blurb_target({"kind": "team", "team": "Fall River Marksmen"})

        self.assertIs(competition_target, competition.objects.get.return_value)
        competition.objects.get.assert_called_once_with(name="Major League Soccer")
        self.assertIs(season_target, season.objects.get.return_value)
        season.objects.get.assert_called_once_with(
            competition__name="American Soccer League (1921-1933)",
            name="1928-1929",
        )
        self.assertIs(team_target, team.objects.get.return_value)
        team.objects.get.assert_called_once_with(name="Fall River Marksmen")

    def test_rejects_unknown_target_kind(self):
        with self.assertRaisesMessage(ValueError, "unknown blurb kind: player"):
            get_blurb_target({"kind": "player"})


class BlurbDatabaseTests(TestCase):
    def test_relates_blurbs_to_each_supported_model(self):
        competition = Competition.objects.create(name="Major League Soccer")
        super_season = SuperSeason.objects.create(name="1996", order=1, order2=1)
        season = Season.objects.create(
            name="1996",
            competition=competition,
            super_season=super_season,
        )
        team = Team.objects.create(name="Dallas Burn", short_name="Dallas Burn")

        for target in (competition, season, team):
            Blurb.objects.create(content_object=target, text="A short piece of history.")
            self.assertEqual(target.blurbs.get().text, "A short piece of history.")
