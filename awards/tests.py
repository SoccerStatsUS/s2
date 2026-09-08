from django.test import SimpleTestCase

from awards.models import Award
from competitions.models import Competition


def award(name, competition_slug=None):
    # Unsaved instances: get_absolute_url only reads the name and the
    # competition's slug, and the assertions are about the URLs.
    return Award(name=name,
                 competition=Competition(slug=competition_slug) if competition_slug else None)


class AwardUrlTests(SimpleTestCase):

    def test_an_award_sits_under_its_competition(self):
        url = award('MVP', 'major-league-soccer').get_absolute_url()

        assert url == '/awards/major-league-soccer/mvp/'

    def test_an_award_with_no_competition_stands_alone(self):
        """The Hall of Fame has nothing to sit under."""
        url = award('US Soccer Hall of Fame').get_absolute_url()

        assert url == '/awards/us-soccer-hall-of-fame/'

    def test_the_same_name_in_two_competitions_stays_apart(self):
        """MVP is the name of sixteen different awards."""
        misl = award('MVP', 'major-indoor-soccer-league-1978-1992').get_absolute_url()
        nasl = award('MVP', 'north-american-soccer-league').get_absolute_url()

        assert misl != nasl

    def test_punctuation_survives_slugging(self):
        url = award("Coach of the Year", 'us-open-cup').get_absolute_url()

        assert url == '/awards/us-open-cup/coach-of-the-year/'
