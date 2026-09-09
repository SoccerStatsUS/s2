from django.test import SimpleTestCase

from news.models import FeedItem, archive_id


class ArchiveIdTests(SimpleTestCase):

    def test_matches_the_oneonta_archive(self):
        """oneonta.archive.item_id on the same url."""
        url = 'http://americansoccernow.com/questionnaires/my-first-questionnaire'

        assert archive_id(url) == '1f55227d77dc'

    def test_a_story_is_addressed_by_its_archive_id(self):
        item = FeedItem(archive_id='1f55227d77dc')

        assert item.get_absolute_url() == '/news/1f55227d77dc/'
