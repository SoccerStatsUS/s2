from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase

from competitions import views
from competitions.models import Competition
from competitions.templatetags.charts import (bar_chart, column_chart, count_chart,
                                              player_goals_chart, timeline_chart)
from competitions.views import (competition_awards, season_postseason, season_standings,
                                show_club_table, stat_leaders)


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


class AttendanceChartTests(SimpleTestCase):

    def season(self, name, average, median, known=10, games=10, partial=False):
        return {'name': name, 'average': average, 'median': median,
                'known': known, 'games': games, 'partial': partial,
                'url': '/c/asl/%s/attendance/' % name}

    def test_each_column_carries_its_own_median(self):
        rows = [self.season('1921', 3000, 2400), self.season('1922', 3100, 3100),
                self.season('1923', 4000, 2000)]

        chart = column_chart(rows, 'Average attendance by season')

        # A season whose median matches its average puts the rule on the cap;
        # a right-skewed one puts it well below.
        base = chart['svg']['base']
        by_name = [c['median']['y'] for c in chart['columns']]
        self.assertLess(by_name[1], by_name[0])
        self.assertLess(by_name[0], by_name[2])
        self.assertTrue(all(y < base for y in by_name))

    def test_median_is_named_in_the_hover_title(self):
        rows = [self.season('1921', 3000, 2400)] * 3

        html = Template('{% load charts %}{% column_chart rows "By season" %}').render(
            Context({'rows': rows}))

        self.assertIn('1921: 3,000 average, 2,400 median, over 10 of 10 games', html)

    def test_a_column_without_a_median_draws_none(self):
        rows = [self.season('1921', 3000, None), self.season('1922', 3100, 3100),
                self.season('1923', 4000, 2000)]

        chart = column_chart(rows, 'By season')

        self.assertIsNone(chart['columns'][0]['median'])

    def test_thin_coverage_is_outlined_only_when_it_sets_a_season_apart(self):
        mixed = [self.season('1921', 3000, 2400, known=9),
                 self.season('1922', 3100, 3100, known=2, partial=True),
                 self.season('1923', 4000, 2000, known=8)]

        self.assertEqual([c['partial'] for c in column_chart(mixed, 'By season')['columns']],
                         [False, True, False])

    def test_a_wholly_thin_chart_fills_rather_than_outlining_everything(self):
        thin = [self.season('1921', 3000, 2400, known=2, partial=True),
                self.season('1922', 3100, 3100, known=1, partial=True),
                self.season('1923', 4000, 2000, known=3, partial=True)]

        chart = column_chart(thin, 'By season')

        self.assertEqual([c['partial'] for c in chart['columns']], [False, False, False])
        self.assertFalse(chart['any_partial'])

    def test_the_rule_is_colored_for_what_it_lands_on(self):
        rows = [self.season('1921', 3000, 2400),                       # inside the fill
                self.season('1922', 3100, 3600),                       # clear of the cap
                self.season('1923', 4000, 2000, known=1, partial=True),
                self.season('1924', 1750, 1750)]                       # flush with the cap

        chart = column_chart(rows, 'By season')

        self.assertEqual([c['median']['css'] for c in chart['columns']],
                         ['on-fill', 'on-surface', 'on-hollow', 'on-surface'])

    def club(self, name, average, median):
        return {'name': name, 'average': average, 'median': median,
                'games': 18, 'total': 18 * average, 'url': '/t/%s/' % name}

    def test_bars_carry_a_median_rule_across_the_bar(self):
        chart = bar_chart([self.club('bethlehem-steel', 4000, 3000),
                           self.club('fall-river', 3000, 2900),
                           self.club('new-york-nationals', 2000, 1900)],
                          'Average home attendance by club')
        first = chart['bars'][0]

        self.assertEqual(first['median']['css'], 'on-fill')
        self.assertEqual(first['median']['y2'] - first['median']['y1'], 14)

    def test_a_median_above_the_longest_bar_still_fits_the_plot(self):
        chart = bar_chart([self.club('brooklyn-wanderers', 4000, 5200),
                           self.club('fall-river', 3000, 2900),
                           self.club('new-york-nationals', 2000, 1900)],
                          'Average home attendance by club')
        longest = chart['bars'][0]

        self.assertLessEqual(longest['median']['x'], chart['svg']['width'])
        self.assertLessEqual(longest['value_x'], chart['svg']['width'])

    def test_a_median_above_the_tallest_column_still_fits_the_plot(self):
        chart = column_chart([self.season('1921', 3000, 5200),
                              self.season('1922', 3100, 3100),
                              self.season('1923', 4000, 2000)], 'By season')
        skewed = chart['columns'][0]

        self.assertGreater(skewed['median']['y'], 0)
        self.assertGreater(skewed['median']['y'], chart['ticks'][-1]['y'])

    def test_the_value_clears_a_median_that_runs_past_the_bar(self):
        chart = bar_chart([self.club('bethlehem-steel', 4000, 3000),
                           self.club('hakoah-all-stars', 3000, 3600),
                           self.club('new-york-nationals', 2000, 1900)],
                          'Average home attendance by club')
        skewed = chart['bars'][1]

        self.assertEqual(skewed['median']['css'], 'on-surface')
        self.assertLess(skewed['median']['x'], skewed['value_x'])


class CompetitionAwardsTests(SimpleTestCase):

    def award(self, name, winners, last=2025):
        """An award given once a season, `winners` of them, ending in `last`."""
        items = [SimpleNamespace(season=SimpleNamespace(order=year, name=str(year)),
                                 year=None)
                 for year in range(last - winners + 1, last + 1)]
        award = MagicMock()
        award.name = name
        award.awarditem_set.select_related.return_value = items
        return award

    def order(self, *awards):
        with patch('competitions.views.Award.objects') as objects:
            objects.filter.return_value.order_by.return_value = list(awards)
            return [row['award'].name for row in competition_awards(object())]

    def test_a_retired_award_falls_below_a_live_one_however_many_winners(self):
        self.assertEqual(
            self.order(self.award('Best XI', 209, last=2014),
                       self.award('Young Player of the Year', 6, last=2025)),
            ['Young Player of the Year', 'Best XI'])

    def test_awards_ending_together_go_by_winners_then_by_name(self):
        self.assertEqual(
            self.order(self.award('Rookie of the Year', 12),
                       self.award('MVP', 30),
                       self.award('Coach of the Year', 30)),
            ['Coach of the Year', 'MVP', 'Rookie of the Year'])

    def test_an_award_with_no_winners_is_left_out(self):
        self.assertEqual(self.order(self.award('Never awarded', 0),
                                    self.award('MVP', 30)), ['MVP'])


class ClubTableTests(SimpleTestCase):
    """
    The club table repeats the chart, so it shows only where the chart cannot
    stand alone.
    """

    def test_hidden_when_the_chart_carries_every_club(self):
        clubs = ['cosmos', 'sounders', 'rowdies', 'timbers']

        self.assertFalse(show_club_table(clubs, clubs))

    def test_shown_when_the_chart_leaves_a_club_out(self):
        clubs = ['cosmos', 'sounders', 'rowdies', 'one-game-wonder']

        self.assertTrue(show_club_table(clubs, clubs[:3]))

    def test_shown_when_there_are_too_few_clubs_to_draw_a_chart(self):
        # bar_chart returns nothing under three rows, so the table is the page.
        clubs = ['cosmos', 'sounders']

        self.assertIsNone(bar_chart([{'name': c, 'average': 100, 'median': 90,
                                      'games': 5, 'total': 500} for c in clubs],
                                    'By club')['svg'])
        self.assertTrue(show_club_table(clubs, clubs))


class ClubTimelineTests(SimpleTestCase):
    """Which clubs played which seasons, drawn a block per season."""

    seasons = ['1968', '1969', '1970', '1971']
    league = Competition(ctype='League', slug='nasl')
    slugs = {name: name for name in seasons}

    def clubs(self, **played):
        return {(name, name.lower()): set(s) for name, s in played.items()}

    def timeline(self, seasons, clubs, competition=None):
        return views.club_timeline(competition or self.league, seasons, clubs)

    def test_rows_run_most_recent_first_then_longest_lived(self):
        timeline = self.timeline(self.seasons, self.clubs(
            Cosmos=['1971'],
            Tornado=['1968', '1969', '1970'],
            Beacons=['1968'],
            Spurs=['1969', '1970']))

        # The Cosmos led on one season because it is the only club left in
        # 1971; the Tornado leads the 1970 leavers on seasons played.
        self.assertEqual([r['name'] for r in timeline['rows']],
                         ['Cosmos', 'Tornado', 'Spurs', 'Beacons'])

    def test_a_club_that_left_and_came_back_keeps_its_gap(self):
        timeline = self.timeline(self.seasons, self.clubs(
            Chiefs=['1968', '1971'], Tornado=['1968', '1969']))
        chiefs = timeline['rows'][0]

        self.assertEqual(chiefs['name'], 'Chiefs')
        self.assertEqual((chiefs['first'], chiefs['last'], chiefs['played']), ('1968', '1971', 2))

        chart = timeline_chart(timeline, 'Clubs')
        self.assertEqual(len(chart['marks'][0]['blocks']), 2)  # not a solid 1968-1971 span

    def test_no_timeline_for_a_cup(self):
        # A cup is a field one-off entrants pass through, not a roll of members.
        clubs = self.clubs(Tornado=['1968', '1969'], Spurs=['1969', '1970'])

        self.assertTrue(self.timeline(self.seasons, clubs)['rows'])
        for ctype in ('Cup', 'Supercup', ''):
            self.assertEqual(
                self.timeline(self.seasons, clubs, Competition(ctype=ctype))['rows'], [],
                'ctype %r should draw no timeline' % ctype)

    def test_no_timeline_for_a_single_season(self):
        self.assertEqual(
            self.timeline(['1968'], self.clubs(A=['1968'], B=['1968']))['rows'], [])

    def test_season_counts_skip_seasons_nobody_played(self):
        counts = views.season_club_counts(self.league, self.seasons, self.clubs(
            Tornado=['1968', '1971'], Spurs=['1968'], Cosmos=['1971']))

        self.assertEqual([(c['name'], c['count']) for c in counts],
                         [('1968', 2), ('1971', 2)])

    def test_each_column_links_to_its_season(self):
        counts = views.season_club_counts(
            self.league, self.seasons,
            self.clubs(Tornado=['1968', '1971'], Spurs=['1968']), self.slugs)

        self.assertEqual(counts[0]['url'], '/c/nasl/1968/')

    def test_each_block_links_to_that_club_in_that_season(self):
        timeline = views.club_timeline(
            self.league, self.seasons,
            self.clubs(Tornado=['1968', '1971'], Spurs=['1968']), self.slugs)
        tornado = next(r for r in timeline['rows'] if r['name'] == 'Tornado')

        self.assertEqual(tornado['urls']['1971'], '/teams/tornado/c/nasl/1971/')
        self.assertEqual(sorted(tornado['urls']), ['1968', '1971'])

    def test_a_club_with_no_slug_gets_no_block_links(self):
        clubs = {('Tornado', ''): {'1968', '1971'}, ('Spurs', 'spurs'): {'1968'}}
        timeline = views.club_timeline(self.league, self.seasons, clubs, self.slugs)
        tornado = next(r for r in timeline['rows'] if r['name'] == 'Tornado')

        self.assertEqual(tornado['urls'], {})


class CountChartTests(SimpleTestCase):

    def counts(self, n):
        """Every column the same height, so each one draws as a full cap."""
        return [{'name': str(1866 + i), 'count': 100} for i in range(n)]

    def bar_width(self, column):
        """
        Read a bar's width back off its cap_path: it opens at x and runs to
        x + width - 4, the corner radius, before the closing curve.
        """
        left = float(column['path'].split('M')[1].split(',')[0])
        right = float(column['path'].split('H')[1].split('Q')[0])
        return right - left + 4

    def test_the_count_is_in_the_title_not_stamped_on_the_column(self):
        rows = [{'name': '1968', 'count': 17}, {'name': '1969', 'count': 5},
                {'name': '1970', 'count': 11}]

        chart = count_chart(rows, 'Clubs by season', 'clubs')
        html = Template('{% load charts %}{% count_chart rows "Clubs by season" "clubs" %}').render(
            Context({'rows': rows}))

        self.assertEqual([c['count'] for c in chart['columns']], [17, 5, 11])
        self.assertIn('1969: 5 clubs', html)
        self.assertNotIn('class="value"', html)

    def test_the_axis_carries_the_values_and_clears_the_tallest_column(self):
        chart = count_chart([{'name': str(y), 'count': 20} for y in range(3)], 'Clubs', 'clubs')

        self.assertEqual(chart['ticks'][0]['text'], '0')
        self.assertGreater(int(chart['ticks'][-1]['text']), 20)

    def test_columns_stay_inside_their_slots(self):
        """
        A century and a half of years is more columns than this chart was first
        written for. A bar wider than its own slot overlaps its neighbours and
        the series renders as one solid block.
        """
        chart = count_chart(self.counts(161), 'Games by year', 'games')
        slot = (chart['svg']['right_edge'] - chart['svg']['left']) / 161

        self.assertLess(slot, 6)  # the case the old 6px floor got wrong
        self.assertLessEqual(max(self.bar_width(c) for c in chart['columns']), slot)

    def test_a_short_series_keeps_its_comfortable_bars(self):
        chart = count_chart(self.counts(31), 'Clubs by season', 'clubs')

        self.assertEqual(round(self.bar_width(chart['columns'][0])), 20)

    def test_the_note_says_what_a_column_counts(self):
        chart = count_chart(self.counts(5), 'Games by year', 'games', note='One a year.')

        self.assertEqual(chart['note'], 'One a year.')
        self.assertEqual(count_chart(self.counts(5), 'c', 'games')['note'], '')

    def test_too_few_to_chart(self):
        self.assertIsNone(count_chart(self.counts(2), 'c', 'games')['svg'])


class CompetitionKindTests(SimpleTestCase):
    """The plain-English line under the competition's name."""

    def kind(self, **kwargs):
        fields = dict(international=False, ctype='League', scope='Country',
                      level=1, area='United States')
        fields.update(kwargs)
        return Competition(**fields).kind()

    def test_divisions_are_named_by_level(self):
        self.assertEqual(self.kind(), 'first-division league')
        self.assertEqual(self.kind(level=2), 'second-division league')

    def test_a_league_with_no_level_on_record_is_just_a_league(self):
        self.assertEqual(self.kind(level=None), 'league')
        self.assertEqual(self.kind(level=9), 'league')

    def test_cups(self):
        self.assertEqual(self.kind(ctype='Cup'), 'cup')
        self.assertEqual(self.kind(ctype='Supercup'), 'supercup')

    def test_club_competitions_above_a_country(self):
        self.assertEqual(self.kind(scope='Confederation', area='CONCACAF'),
                         'continental club competition')
        self.assertEqual(self.kind(scope='World', area='Earth'),
                         'international club competition')

    def test_national_team_play(self):
        self.assertEqual(self.kind(international=True, ctype='Cup'),
                         'national-team competition')

    def test_nothing_claimed_where_the_record_is_silent(self):
        self.assertIsNone(self.kind(ctype='', scope='', level=None, area=''))


class CompetitionTierTests(SimpleTestCase):
    """The five bands the season goal chart stacks, as the data records them."""

    def tier(self, **kwargs):
        fields = dict(international=False, ctype='League', scope='Country',
                      level=1, area='United States')
        fields.update(kwargs)
        return Competition(**fields).tier()

    def test_united_states_first_division(self):
        self.assertEqual(self.tier(), 'us_d1')

    def test_foreign_first_division(self):
        self.assertEqual(self.tier(area='Costa Rica'), 'other_d1')
        self.assertEqual(self.tier(area='England'), 'other_d1')

    def test_lower_and_unranked_leagues(self):
        self.assertEqual(self.tier(level=2), 'non_d1')
        self.assertEqual(self.tier(level=None), 'non_d1')  # MLS Reserve League

    def test_cups(self):
        self.assertEqual(self.tier(ctype='Cup'), 'cup')
        self.assertEqual(self.tier(ctype='Supercup'), 'cup')

    def test_continental_club_tournaments_recorded_as_leagues_are_cups(self):
        # CONCACAF Champions League, Leagues Cup, North American SuperLiga.
        self.assertEqual(self.tier(scope='Confederation', area='CONCACAF'), 'cup')
        self.assertEqual(self.tier(scope='World', area='Earth'), 'cup')

    def test_national_team_play(self):
        self.assertEqual(self.tier(international=True, ctype='Cup'), 'international')
        self.assertEqual(self.tier(international=True, ctype='', scope='World',
                                   level=None, area='Earth'), 'international')


class PlayerGoalsChartTests(SimpleTestCase):

    rows = [
        {'name': '1996', 'goals': 34, 'games': 36,
         'tiers': {'us_d1': 27, 'cup': 4, 'international': 3}},
        {'name': '1997', 'goals': 10, 'games': 28,
         'tiers': {'other_d1': 8, 'cup': 2}},
        {'name': '1998', 'goals': 22, 'games': 36,
         'tiers': {'us_d1': 20, 'non_d1': 2}},
    ]

    def test_renders_season_goal_totals(self):
        chart = player_goals_chart(self.rows, 'Goals by season')
        html = Template(
            '{% load charts %}{% player_goals_chart rows "Goals by season" %}'
        ).render(Context({'rows': self.rows}))

        self.assertEqual([column['goals'] for column in chart['columns']],
                         [34, 10, 22])
        self.assertIn('1996, US D1: 27 goals', html)
        self.assertIn('1996, international: 3 goals', html)
        self.assertIn('1998, non-D1 league: 2 goals', html)
        self.assertIn('Goals by season', html)

    def test_stacks_tiers_from_the_baseline_up(self):
        chart = player_goals_chart(self.rows, 'Goals by season')
        column = chart['columns'][0]

        self.assertEqual([segment['css'] for segment in column['segments']],
                         ['us-d1', 'cup', 'international'])

    def test_legend_lists_only_the_tiers_scored_in(self):
        chart = player_goals_chart(self.rows, 'Goals by season')

        self.assertEqual([key['label'] for key in chart['keys']],
                         ['US D1', 'other D1', 'non-D1 league', 'cup', 'international'])

        chart = player_goals_chart(
            [dict(row, tiers={'us_d1': row['goals']}) for row in self.rows],
            'Goals by season')
        self.assertEqual([key['label'] for key in chart['keys']], ['US D1'])


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
