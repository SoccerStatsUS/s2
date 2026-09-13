from unittest.mock import patch

from django.test import SimpleTestCase

from build.generate import stadium_standings
from build.getters import keep_news_item, make_bio_getter, make_city_getter


class BioGetterTests(SimpleTestCase):
    @patch('build.getters.Bio')
    def test_matches_names_ignoring_diacritics(self, bio):
        bio.objects.bio_dict.return_value = {'Josef Martínez': 7}

        get_bio = make_bio_getter()

        self.assertEqual(get_bio('Josef Martinez'), 7)
        bio.objects.create.assert_not_called()

    @patch('build.getters.Bio')
    def test_creates_only_one_bio_for_equivalent_unknown_names(self, bio):
        bio.objects.bio_dict.return_value = {}
        bio.objects.create.return_value.id = 8

        get_bio = make_bio_getter()

        self.assertEqual(get_bio('John\N{NO-BREAK SPACE}McGuire'), 8)
        self.assertEqual(get_bio('john mcguire'), 8)
        bio.objects.create.assert_called_once_with(name='John\N{NO-BREAK SPACE}McGuire', hall_of_fame=False)


class NewsFilterTests(SimpleTestCase):
    def row(self, source, title, summary=''):
        return {'source': source, 'title': title, 'summary': summary}

    def test_american_sources_pass(self):
        self.assertTrue(keep_news_item(self.row('American Soccer Now', 'Euro Notebook')))
        self.assertTrue(keep_news_item(self.row('du Nord', 'Some Soccer News for Jan 31, 2018')))

    def test_espn_needs_an_american_angle(self):
        self.assertTrue(keep_news_item(self.row('ESPN.com', 'MLS sets record for transfer revenue in 2026')))
        self.assertTrue(keep_news_item(self.row('ESPN.com', 'Pochettino names squad', 'The U.S. coach picked 26.')))
        self.assertTrue(keep_news_item(self.row('ESPN.com', 'Leagues Cup final set')))
        self.assertFalse(keep_news_item(self.row('ESPN.com', 'Barcola limps out of Liverpool home debut in UCL')))
        self.assertFalse(keep_news_item(self.row('ESPN.com', 'Stuttgart hat trick', 'Bundesliga notes')))


class CityGetterTests(SimpleTestCase):
    @patch('build.getters.City')
    @patch('build.getters.Country')
    @patch('build.getters.State')
    @patch('build.getters.soccer_db')
    def test_looks_a_location_up_once(self, soccer_db, state, country, city):
        soccer_db.states.find.return_value = [{'abbreviation': 'TX', 'name': 'Texas', 'country': 'United States'}]
        soccer_db.countries.find.return_value = [{'name': 'United States'}]

        get_city = make_city_getter()

        self.assertIs(get_city('Dallas, TX'), city.objects.get.return_value)
        self.assertIs(get_city('Dallas, TX'), city.objects.get.return_value)
        state.objects.get.assert_called_once_with(name='Texas')
        country.objects.get.assert_called_once_with(name='United States')
        city.objects.get.assert_called_once()
        self.assertIsNone(get_city(''))


class StadiumStandingTests(SimpleTestCase):
    def test_counts_both_sides_of_every_game(self):
        rows = [
            (1, 10, 20, 'w', 'l', 3, 1),
            (1, 20, 10, 't', 't', 2, 2),
            (1, 10, 30, None, None, None, None),
            (2, 10, 20, 'l', 'w', 0, 1),
        ]
        by_key = {(s['stadium_id'], s['team_id']): s for s in stadium_standings(rows)}

        self.assertEqual(by_key[(1, 10)], {
            'team_id': 10, 'stadium_id': 1, 'games': 2, 'wins': 1, 'losses': 0, 'ties': 1,
            'goals_for': 5, 'goals_against': 3})
        self.assertEqual(by_key[(2, 20)], {
            'team_id': 20, 'stadium_id': 2, 'games': 1, 'wins': 1, 'losses': 0, 'ties': 0,
            'goals_for': 1, 'goals_against': 0})
        self.assertEqual(by_key[(1, 30)]['games'], 0)
        self.assertEqual(len(by_key), 5)
