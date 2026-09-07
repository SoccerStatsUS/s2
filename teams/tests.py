import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from teams.views import team_games


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
        first_game = SimpleNamespace(id=1, date=datetime.date(1996, 4, 13))
        last_game = SimpleNamespace(id=2, date=datetime.date(2026, 9, 5))
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
