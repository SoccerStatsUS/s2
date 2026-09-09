from django.test import SimpleTestCase

from news.models import FeedItem, archive_id, mentions, name_lookup


class ArchiveIdTests(SimpleTestCase):

    def test_matches_the_oneonta_archive(self):
        """oneonta.archive.item_id on the same url."""
        url = 'http://americansoccernow.com/questionnaires/my-first-questionnaire'

        assert archive_id(url) == '1f55227d77dc'

    def test_a_story_is_addressed_by_its_archive_id(self):
        item = FeedItem(archive_id='1f55227d77dc')

        assert item.get_absolute_url() == '/news/1f55227d77dc/'


class MentionTests(SimpleTestCase):
    lookup = name_lookup({
        'Landon Donovan': 1,
        'Donovan': 2,
        'Josef Martínez': 3,
        "Shane O'Brien": 4,
        'Carlos Vela': 5,
        'Carlos Vela Garrido': 6,
        '1-1.': 7,
        'S. Day': 8,
    })

    def test_a_full_name_in_the_text(self):
        assert mentions('Landon Donovan scored twice.', self.lookup) == [1]

    def test_a_one_word_name_never_matches(self):
        assert mentions('Donovan scored twice.', self.lookup) == []

    def test_scores_and_initials_filed_as_people_never_match(self):
        assert mentions('It ended 1-1. S. Day', self.lookup) == []
        assert mentions("Father's Day", self.lookup) == []

    def test_diacritics_and_case_fold(self):
        assert mentions('JOSEF MARTINEZ was back.', self.lookup) == [3]
        assert mentions('Josef Martínez was back.', self.lookup) == [3]

    def test_punctuation_around_and_inside_a_name(self):
        assert mentions("...Shane O'Brien's header (Donovan assisting).", self.lookup) == [4]
        assert mentions("Shane O’Brien", self.lookup) == [4]

    def test_the_longest_name_wins(self):
        assert mentions('Carlos Vela Garrido started.', self.lookup) == [6]
        assert mentions('Carlos Vela started.', self.lookup) == [5]

    def test_each_person_once_in_order_of_first_mention(self):
        text = 'Carlos Vela found Landon Donovan; Carlos Vela again.'
        assert mentions(text, self.lookup) == [5, 1]
