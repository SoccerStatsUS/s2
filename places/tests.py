from types import SimpleNamespace

from django.test import SimpleTestCase

from places.models import playing_time_by_country


class StatRows(list):
    """As much queryset as minutes_by_country asks for."""

    def select_related(self, *args):
        return self


def stat(minutes, country=None, city_country=None, games=1):
    player = SimpleNamespace(
        birth_country=country,
        birthplace=SimpleNamespace(country=city_country) if city_country else None,
    )
    return SimpleNamespace(minutes=minutes, games_played=games, player=player)


class country(object):
    """Hashable, because minutes_by_country groups on the country itself."""

    def __init__(self, name):
        self.name = name
        self.slug = name.lower()


class MinutesByCountryTests(SimpleTestCase):

    def test_groups_minutes_and_orders_by_share(self):
        usa, arg = country('United States'), country('Argentina')
        rows = playing_time_by_country(StatRows([
            stat(900, usa), stat(600, arg), stat(1500, usa),
        ]))['rows']

        assert [(r['name'], r['value']) for r in rows] == [
            ('United States', 2400), ('Argentina', 600)]
        assert rows[0]['percent'] == 80.0

    def test_birthplace_stands_in_for_a_missing_birth_country(self):
        rows = playing_time_by_country(StatRows([stat(90, None, country('Ireland'))]))['rows']

        assert [r['name'] for r in rows] == ['Ireland']

    def test_unattributed_minutes_get_their_own_row(self):
        rows = playing_time_by_country(StatRows([stat(750, country('Jamaica')), stat(250)]))['rows']

        assert rows[-1]['name'] == 'not recorded'
        assert rows[-1]['country'] is None
        assert rows[-1]['percent'] == 25.0

    def test_nothing_to_say_when_no_minute_resolves(self):
        """A single 'not recorded' row at 100% is worse than no breakdown."""
        assert playing_time_by_country(StatRows([stat(900), stat(600)]))['rows'] == []

    def test_players_who_did_not_play_are_left_out(self):
        rows = playing_time_by_country(StatRows([
            stat(900, country('Wales')), stat(0, country('Peru'), games=0),
            stat(None, country('Chile'), games=0),
        ]))['rows']

        assert [r['name'] for r in rows] == ['Wales']


class MeasureTests(SimpleTestCase):
    """
    The NASL, the ASL and the indoor leagues record appearances for every
    season and minutes for none.
    """

    def test_minutes_where_they_are_recorded(self):
        result = playing_time_by_country(StatRows([
            stat(900, country('Peru'), games=10), stat(450, country('Chile'), games=5)]))

        assert result['measure'] == 'minutes'
        assert [r['value'] for r in result['rows']] == [900, 450]

    def test_games_where_minutes_are_not(self):
        result = playing_time_by_country(StatRows([
            stat(None, country('Peru'), games=10), stat(None, country('Chile'), games=5)]))

        assert result['measure'] == 'games'
        assert [r['value'] for r in result['rows']] == [10, 5]

    def test_a_season_half_covered_falls_back(self):
        """Counting minutes there would score the uncovered players at zero."""
        result = playing_time_by_country(StatRows([
            stat(900, country('Peru'), games=10),
            stat(None, country('Chile'), games=9),
            stat(None, country('Brazil'), games=8)]))

        assert result['measure'] == 'games'
        assert [r['name'] for r in result['rows']] == ['Peru', 'Chile', 'Brazil']
