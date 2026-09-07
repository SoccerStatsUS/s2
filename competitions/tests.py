from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase

from competitions.templatetags.charts import player_goals_chart
from competitions.views import season_postseason, season_standings, stat_leaders


class QueryRows(list):
    def exists(self):
        return bool(self)

    def exclude(self, **kwargs):
        name, value = next(iter(kwargs.items()))
        return QueryRows(row for row in self if getattr(row, name) != value)


class SeasonStandingsTests(SimpleTestCase):
    def test_uses_most_common_historical_team_name(self):
        standing = SimpleNamespace(team_id=1, team=SimpleNamespace(name='FC Dallas'))
        season = MagicMock()
        standings = season.standing_set.filter.return_value.select_related.return_value
        standings.order_by.return_value = [standing]
        season.game_set.values_list.return_value = [
            (1, 'Dallas Burn', 2, 'Columbus Crew'),
            (1, 'Dallas Burn', 3, 'D.C. United'),
        ]

        standings = season_standings(season)

        season.standing_set.filter.return_value.select_related.return_value.order_by.assert_called_once_with(
            '-points', '-wins', 'team__name'
        )
        self.assertEqual(standings[0].team_display_name, 'Dallas Burn')

    def test_standings_template_ignores_conference_and_uses_historical_name(self):
        team = SimpleNamespace(name='FC Dallas', slug='')
        standing = SimpleNamespace(
            stage='',
            group='Western Conference',
            team=team,
            team_display_name='Dallas Burn',
            games=32,
            wins=12,
            shootout_wins=5,
            ties=None,
            shootout_losses=3,
            losses=12,
            points=41,
            goals_for=50,
            goals_against=48,
        )
        template = Template(
            "{% load standings %}{% standings_table standings 'competition,season' %}"
        )

        html = template.render(Context({'standings': QueryRows([standing])}))

        self.assertNotIn('Western Conference', html)
        self.assertEqual(html.count('<table class="standings">'), 1)
        self.assertIn('Dallas Burn', html)
        self.assertNotIn('FC Dallas', html)


class SeasonLeaderTests(SimpleTestCase):
    def test_stat_leaders_aggregates_player_totals(self):
        stats = MagicMock()

        stat_leaders(stats, 'goals')

        stats.filter.assert_called_once_with(goals__gt=0)
        values = stats.filter.return_value.values
        values.assert_called_once_with('player_id', 'player__name', 'player__slug')
        annotation = values.return_value.annotate.call_args.kwargs['value']
        self.assertEqual(annotation.source_expressions[0].name, 'goals')
        values.return_value.annotate.return_value.order_by.assert_called_once_with(
            '-value', 'player__name'
        )

    def test_leaders_template_renders_compact_categories(self):
        leader_groups = [
            {
                'label': 'Goals',
                'rows': [
                    {'player__name': 'Roy Lassiter', 'player__slug': '', 'value': 27}
                ],
            },
            {
                'label': 'Assists',
                'rows': [
                    {'player__name': 'Carlos Valderrama', 'player__slug': '', 'value': 17}
                ],
            },
        ]
        template = Template(
            '{% include "competitions/season/leaders.html" %}'
        )

        html = template.render(Context({'leader_groups': leader_groups}))

        self.assertIn('Goals', html)
        self.assertIn('Roy Lassiter', html)
        self.assertIn('<strong>27</strong>', html)
        self.assertIn('Assists', html)
        self.assertIn('Carlos Valderrama', html)

    def test_competition_detail_uses_compact_leader_groups(self):
        relation = MagicMock()
        relation.exists.return_value = False
        competition = SimpleNamespace(
            name='Major League Soccer',
            abbreviation='MLS',
            slug='major-league-soccer',
            after=relation,
            before=relation,
            season_set=SimpleNamespace(reverse=[]),
        )
        leader_groups = [
            {
                'label': 'Goals',
                'rows': [
                    {'player__name': 'Chris Wondolowski',
                     'player__slug': 'chris-wondolowski', 'value': 171}
                ],
            },
        ]
        games = MagicMock()
        games.values_list.return_value = []
        games.__iter__.return_value = iter([])

        html = render_to_string('competitions/competition/detail.html', {
            'competition': competition,
            'leader_groups': leader_groups,
            'games': games,
            'big_winners': [],
            'awards': [],
        })

        self.assertIn('Career leaders', html)
        self.assertIn('Chris Wondolowski', html)
        self.assertIn('<strong>171</strong>', html)
        self.assertIn('complete stats', html)
        self.assertNotIn('<table class="stats">', html)


class PlayerGoalsChartTests(SimpleTestCase):

    def test_renders_season_goal_totals(self):
        rows = [
            {'name': '1996', 'goals': 34, 'games': 36},
            {'name': '1997', 'goals': 10, 'games': 28},
            {'name': '1998', 'goals': 22, 'games': 36},
        ]

        chart = player_goals_chart(rows, 'Club goals by season')
        html = Template(
            '{% load charts %}{% player_goals_chart rows "Club goals by season" %}'
        ).render(Context({'rows': rows}))

        self.assertEqual([column['goals'] for column in chart['columns']],
                         [34, 10, 22])
        self.assertIn('1996: 34 goals in 36 games', html)
        self.assertIn('Club goals by season', html)


class SeasonPostseasonTests(SimpleTestCase):
    @patch('competitions.views.Season.objects')
    def test_finds_playoff_season_and_championship_game(self, seasons):
        season = SimpleNamespace(
            competition=SimpleNamespace(slug='major-league-soccer'),
            super_season=object(),
        )
        playoff_season = MagicMock()
        championship_game = MagicMock()
        seasons.filter.return_value.select_related.return_value.first.return_value = playoff_season
        games = playoff_season.game_set.filter.return_value
        games.select_related.return_value.order_by.return_value.first.return_value = championship_game

        postseason = season_postseason(season)

        seasons.filter.assert_called_once_with(
            super_season=season.super_season,
            competition__slug='mls-cup-playoffs',
        )
        playoff_season.game_set.filter.assert_called_once_with(
            round__in=('MLS Cup', 'Final', 'Championship'),
            not_played=False,
        )
        self.assertEqual(postseason['season'], playoff_season)
        self.assertEqual(postseason['championship_game'], championship_game)

    @patch('competitions.views.Season.objects')
    def test_uses_last_playoff_game_when_rounds_are_missing(self, seasons):
        season = SimpleNamespace(
            competition=SimpleNamespace(slug='major-league-soccer'),
            super_season=object(),
        )
        playoff_season = MagicMock()
        championship_game = MagicMock()
        playoff_season.champion.return_value = object()
        seasons.filter.return_value.select_related.return_value.first.return_value = playoff_season
        labeled_games = playoff_season.game_set.filter.return_value
        labeled_games.select_related.return_value.order_by.return_value.first.return_value = None
        dated_games = playoff_season.game_set.exclude.return_value.exclude.return_value
        dated_games.select_related.return_value.order_by.return_value.first.return_value = championship_game

        postseason = season_postseason(season)

        playoff_season.game_set.exclude.assert_called_once_with(date=None)
        playoff_season.game_set.exclude.return_value.exclude.assert_called_once_with(
            not_played=True
        )
        self.assertEqual(postseason['championship_game'], championship_game)

    @patch('competitions.views.Season.objects')
    def test_does_not_infer_championship_before_champion_is_known(self, seasons):
        season = SimpleNamespace(
            competition=SimpleNamespace(slug='major-league-soccer'),
            super_season=object(),
        )
        playoff_season = MagicMock()
        playoff_season.champion.return_value = None
        seasons.filter.return_value.select_related.return_value.first.return_value = playoff_season
        labeled_games = playoff_season.game_set.filter.return_value
        labeled_games.select_related.return_value.order_by.return_value.first.return_value = None

        postseason = season_postseason(season)

        playoff_season.game_set.exclude.assert_not_called()
        self.assertIsNone(postseason['championship_game'])

    def test_postseason_template_links_playoffs_and_shows_final(self):
        galaxy = SimpleNamespace(slug='los-angeles-galaxy')
        united = SimpleNamespace(slug='dc-united')
        game = SimpleNamespace(
            id=1,
            round='MLS Cup',
            date=None,
            team1=galaxy,
            team1_original_name='Los Angeles Galaxy',
            team2=united,
            team2_original_name='D.C. United',
            winner=united,
            score_or_result='2 - 3',
        )
        postseason = {
            'season': SimpleNamespace(
                slug='1996',
                competition=SimpleNamespace(
                    slug='mls-cup-playoffs', name='MLS Cup Playoffs'
                ),
            ),
            'championship_game': game,
        }
        template = Template(
            '{% include "competitions/season/postseason.html" %}'
        )

        html = template.render(Context({'postseason': postseason}))

        self.assertIn('/c/mls-cup-playoffs/1996/', html)
        self.assertIn('MLS Cup', html)
        self.assertIn('Los Angeles Galaxy', html)
        self.assertIn('<strong><a href="/teams/dc-united/">D.C. United</a></strong>', html)
        self.assertIn('2 - 3', html)
