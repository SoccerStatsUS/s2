import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from competitions.templatetags.charts import ladder_chart
from teams.views import season_year, team_games


class TeamGamesTests(SimpleTestCase):

    @patch('teams.views.render')
    @patch('teams.views.TempGameStanding')
    @patch('teams.views.Paginator')
    @patch('teams.views.TeamGameForm')
    @patch('teams.views.Game')
    @patch('teams.views.Team')
    def test_paginates_games_without_limiting_standings(
            self, team_model, game_model, form_class, paginator,
            standing_class, render):
        request = RequestFactory().get('/teams/fc-dallas/games/', {'page': '2'})
        team = team_model.objects.by_slug.return_value
        form_class.return_value.is_valid.return_value = False
        games = game_model.objects.team_filter.return_value.select_related.return_value.order_by.return_value
        newest = MagicMock()
        oldest = MagicMock()
        games.filter.return_value.__getitem__.return_value = [newest, oldest]
        page = MagicMock()
        paginator.return_value.get_page.return_value = page

        team_games(request, 'fc-dallas')

        standing_class.assert_called_once_with(games, team)
        self.assertEqual(render.call_args.args[2]['chart_games'], [oldest, newest])
        paginator.assert_called_once_with(games, 100)
        paginator.return_value.get_page.assert_called_once_with('2')
        context = render.call_args.args[2]
        self.assertIs(context['games'], page.object_list)
        self.assertIs(context['page'], page)


class TeamDetailTests(SimpleTestCase):

    def test_renders_summary_and_honors(self):
        aliases = MagicMock()
        aliases.exists.return_value = False
        team = SimpleNamespace(
            name='LA Galaxy',
            slug='la-galaxy',
            founded=datetime.date(1995, 1, 1),
            dissolved=None,
            city=None,
            teamalias_set=aliases,
        )
        competition = SimpleNamespace(
            name='MLS Cup Playoffs',
            abbreviation='MLS Cup',
            slug='mls-cup-playoffs',
        )
        season = SimpleNamespace(name='2024', slug='2024', competition=competition)
        award = SimpleNamespace(
            id=1,
            name='MLS Cup',
            competition=competition,
        )
        awards = [SimpleNamespace(season=season, year=None, award=award)]
        alltime = SimpleNamespace(wins=333, ties=163, losses=243)
        first_game = SimpleNamespace(
            id=1, date=datetime.date(1996, 4, 13),
            get_absolute_url=lambda: '/games/1996-04-13/major-league-soccer/a-v-b/')
        last_game = SimpleNamespace(
            id=2, date=datetime.date(2026, 9, 5),
            get_absolute_url=lambda: '/games/2026-09-05/major-league-soccer/a-v-b/')
        recent_games = MagicMock()
        recent_games.values_list.return_value = []
        recent_games.__iter__.return_value = iter([])

        html = render_to_string('teams/detail.html', {
            'team': team,
            'games_count': 1147,
            'alltime': alltime,
            'awards': awards,
            'first_game': first_game,
            'last_game': last_game,
            'competition_standings': [],
            'league_standings': [],
            'game_leaders': None,
            'goal_leaders': None,
            'recent_games': recent_games,
        })

        self.assertIn('aria-label="Recorded team totals"', html)
        self.assertIn('<dd>1,147</dd>', html)
        self.assertIn('<dt>honors</dt><dd>1</dd>', html)
        self.assertIn('founded', html)
        self.assertIn('first recorded game', html)
        self.assertIn('latest recorded game', html)
        self.assertIn('<h2>Honors</h2>', html)
        self.assertIn('MLS Cup', html)


class SeasonYearTests(SimpleTestCase):

    def test_split_year_season_lands_on_the_year_it_began(self):
        assert season_year('1924-1925') == 1924

    def test_calendar_year_season(self):
        assert season_year('2004') == 2004

    def test_a_season_named_something_else_has_no_year(self):
        # Better no block than a block on the wrong year.
        assert season_year('Spring') is None
        assert season_year('') is None
        assert season_year(None) is None


class ClubLadderChartTests(SimpleTestCase):

    def entry(self, year, level):
        return {'year': year, 'level': level, 'season': str(year),
                'competition': 'A League', 'url': '/x/'}

    def test_years_run_unbroken_so_a_gap_stays_visible(self):
        chart = ladder_chart([self.entry(1970, 1), self.entry(1975, 1)], 'c')

        assert chart['first'] == 1970 and chart['last'] == 1975
        # One row, two blocks, four empty years between them.
        assert [row['count'] for row in chart['rows']] == [2]

    def test_only_the_levels_used_get_a_row(self):
        chart = ladder_chart([self.entry(1970, 1), self.entry(1971, 4)], 'c')

        assert [row['name'] for row in chart['rows']] == ['1st division', '4th division']

    def test_a_league_with_no_level_keeps_its_seasons_in_a_band_of_its_own(self):
        chart = ladder_chart([self.entry(1970, 1), self.entry(1971, None)], 'c')

        assert chart['unplaced'] is True
        assert [row['name'] for row in chart['rows']] == ['1st division', 'level not recorded']
        assert [row['placed'] for row in chart['rows']] == [True, False]

    def test_one_season_is_not_a_chart(self):
        assert ladder_chart([self.entry(1970, 1)], 'c')['svg'] is None
