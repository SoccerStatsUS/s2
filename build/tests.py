from unittest.mock import patch

from django.test import SimpleTestCase

from build.getters import keep_news_item, make_bio_getter


class BioGetterTests(SimpleTestCase):
    @patch('build.getters.Bio')
    def test_matches_names_ignoring_diacritics(self, bio):
        bio.objects.bio_dict.return_value = {'Josef Martínez': 7}

        get_bio = make_bio_getter()

        self.assertEqual(get_bio('Josef Martinez'), 7)
        bio.objects.find.assert_not_called()

    @patch('build.getters.Bio')
    def test_creates_only_one_bio_for_equivalent_unknown_names(self, bio):
        bio.objects.bio_dict.return_value = {}
        bio.objects.find.return_value.id = 8

        get_bio = make_bio_getter()

        self.assertEqual(get_bio('John\N{NO-BREAK SPACE}McGuire'), 8)
        self.assertEqual(get_bio('john mcguire'), 8)
        bio.objects.find.assert_called_once_with('John\N{NO-BREAK SPACE}McGuire')


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
