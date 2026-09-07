from unittest.mock import MagicMock, patch

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
