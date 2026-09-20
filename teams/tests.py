import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from competitions.templatetags.charts import ladder_chart
from competitions.models import Competition, Season
from games.models import Game
from standings.models import Standing
from teams.models import Team
from teams.views import season_year, team_competition_detail, team_games


class TeamCompetitionTests(SimpleTestCase):

    def test_empty_competition_page_renders(self):
        team = Team(id=1, name='Brooklyn Wanderers', slug='brooklyn-wanderers')
        competition = Competition(id=1, name='ASL', slug='asl')
        request = RequestFactory().get('/teams/brooklyn-wanderers/c/asl/')
        with (
            patch('teams.views.Team.objects.by_slug', return_value=team),
            patch('teams.views.get_object_or_404', return_value=competition),
            patch('teams.views.Game.objects.team_filter', return_value=Game.objects.none()),
            patch('teams.views.Standing.objects.filter', return_value=Standing.objects.none()),
        ):
            response = team_competition_detail(request, team.slug, competition.slug)

        self.assertContains(response, 'Brooklyn Wanderers in ASL')
        self.assertContains(response, 'No games on record')
        self.assertContains(response, 'href="/c/asl/"')

    def test_season_records_and_results_render(self):
        team = Team(id=1, name='Brooklyn Wanderers', slug='brooklyn-wanderers')
        opponent = Team(id=2, name='Fall River Marksmen', slug='fall-river-marksmen')
        competition = Competition(id=1, name='ASL', slug='asl')
        season = Season(id=1, name='1930 Fall', slug='1930-fall', competition=competition)
        standing = Standing(team=team, competition=competition, season=season,
                            games=30, wins=10, ties=7, losses=13)
        game = Game(id=1, date=datetime.date(1930, 12, 14), competition=competition,
                    season=season, team1=team, team2=opponent,
                    team1_original_name='Brooklyn Wanderers',
                    team2_original_name='Fall River Marksmen',
                    team1_score=2, team2_score=3)
        game.prefetched_goals = []
        game._prefetched_objects_cache = {'sources': []}
        games = MagicMock()
        games.values_list.return_value = []
        games.select_related.return_value.prefetch_related.return_value = [game]

        html = render_to_string('teams/competition_detail.html', {
            'team': team, 'competition': competition,
            'standings': [standing], 'games': games,
            'page': SimpleNamespace(paginator=SimpleNamespace(count=1)),
        })

        self.assertIn('Season records', html)
        self.assertIn('1930 Fall', html)
        self.assertIn('Fall River Marksmen', html)
        self.assertIn('href="%s"' % game.get_absolute_url(), html)

    @patch('teams.views.render')
    @patch('teams.views.Paginator')
    @patch('teams.views.Standing')
    @patch('teams.views.Game')
    @patch('teams.views.get_object_or_404')
    @patch('teams.views.Team')
    def test_scopes_records_and_games_to_competition_and_paginates(
            self, team_model, get_competition, game_model, standing_model,
            paginator, render):
        request = RequestFactory().get('/teams/brooklyn-wanderers/c/asl/', {'page': '2'})
        team = team_model.objects.by_slug.return_value
        competition = get_competition.return_value

        team_competition_detail(request, 'brooklyn-wanderers', 'asl')

        game_model.objects.team_filter.assert_called_once_with(team)
        game_model.objects.team_filter.return_value.filter.assert_called_once_with(
            competition=competition)
        standing_model.objects.filter.assert_called_once_with(
            team=team, competition=competition, final=True)
        paginator.return_value.get_page.assert_called_once_with('2')
        context = render.call_args.args[2]
        self.assertIs(context['games'], paginator.return_value.get_page.return_value.object_list)


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
            get_absolute_url=lambda: '/awards/1/',
        )
        awards = [SimpleNamespace(season=season, year=None, award=award)]
        honors = [{'award': award, 'label': 'MLS Cup', 'items': awards}]
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
            'honors': honors,
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
        self.assertIn('<ul class="honors-list">', html)
        self.assertIn('<a href="/awards/1/">MLS Cup</a>', html)
        self.assertIn('<span class="honor-years">(<a href="/c/mls-cup-playoffs/2024/">2024</a>)</span>', html)


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


class NameKeyTests(SimpleTestCase):
    """
    The QA page groups names that differ only by filler, accents, punctuation
    or word order.
    """

    def test_filler_accents_and_order_fall_away(self):
        from teams.views import name_key

        assert name_key('Aston Villa FC') == name_key('Aston Villa')
        assert name_key('Club Atlético de Madrid') == name_key('Atletico Madrid')
        assert name_key('AC St. Louis') == name_key('St. Louis AC')

    def test_distinct_clubs_keep_distinct_keys(self):
        from teams.views import name_key

        assert name_key('Portland Timbers') != name_key('Portland Timbers 2')
        assert name_key('United States U-20') != name_key('United States U-23')

    def test_groups_skip_singletons_and_shared_slugs(self):
        from teams.views import name_groups

        teams = [
            SimpleNamespace(name='Aston Villa', slug='aston-villa'),
            SimpleNamespace(name='Aston Villa FC', slug='aston-villa-fc'),
            SimpleNamespace(name='Barnsley', slug='barnsley'),
            SimpleNamespace(name='Central Cordoba', slug='central-cordoba'),
            SimpleNamespace(name='Central Córdoba', slug='central-cordoba'),
        ]

        groups = name_groups(teams)

        assert [[t.name for t in group] for _, group in groups] == [['Aston Villa', 'Aston Villa FC']]
