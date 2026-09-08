from django.test import SimpleTestCase

from sources.models import Source


class SourceUrlTests(SimpleTestCase):

    def test_a_source_is_addressed_by_its_name(self):
        url = Source(name='Roger Allaway Personal Notes').get_absolute_url()

        assert url == '/sources/roger-allaway-personal-notes/'

    def test_a_year_range_survives_slugging(self):
        """Three Spalding guides differ only by the years on the cover."""
        url = Source(name='Spalding Soccer Guide 1915-1916').get_absolute_url()

        assert url == '/sources/spalding-soccer-guide-1915-1916/'

    def test_guides_from_different_years_stay_apart(self):
        a = Source(name='Spalding Soccer Guide 1915-1916').get_absolute_url()
        b = Source(name='Spalding Soccer Guide 1917-1918').get_absolute_url()

        assert a != b

    def test_punctuation_and_case_are_dropped(self):
        url = Source(name="Spalding's Official Soccer Football Guide").get_absolute_url()

        assert url == '/sources/spaldings-official-soccer-football-guide/'

    def test_a_domain_breaks_on_the_period(self):
        """Half the sources are named for a website; slugify alone glues the tld on."""
        url = Source(name='NewspaperArchive.com').get_absolute_url()

        assert url == '/sources/newspaperarchive-com/'

    def test_a_domain_stays_apart_from_what_follows_it(self):
        """Three USL sources share a domain and differ only in the trailing words."""
        a = Source(name='USLsoccer.com USL-1').get_absolute_url()
        b = Source(name='USLsoccer.com USL Pro').get_absolute_url()

        assert a == '/sources/uslsoccer-com-usl-1/'
        assert b == '/sources/uslsoccer-com-usl-pro/'
