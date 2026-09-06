from unittest.mock import patch

from django.test import SimpleTestCase

from build.getters import make_bio_getter


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
