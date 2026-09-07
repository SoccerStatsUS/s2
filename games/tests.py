import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from games.management.commands.errordigest import format_digest, parse
from games.templatetags.result_chart import recent_results_chart
from games.views import search

JOURNAL = """\
2026-08-22T06:25:39+00:00 bert gunicorn[11]: Internal Server Error: /bios/jimmy-drain/
2026-08-22T06:25:39+00:00 bert gunicorn[11]: Traceback (most recent call last):
2026-08-22T06:25:39+00:00 bert gunicorn[11]:   File "views.py", line 9, in bio_detail
2026-08-22T06:25:39+00:00 bert gunicorn[11]:     x = bio.games_played
2026-08-22T06:25:39+00:00 bert gunicorn[11]:         ^^^^^^^^^^^^^^^^
2026-08-22T06:25:41+00:00 bert gunicorn[12]: Internal Server Error: /places/cities/
2026-08-22T06:25:39+00:00 bert gunicorn[11]: AttributeError: 'NoneType' object has no attribute 'games_played'
2026-08-22T06:25:41+00:00 bert gunicorn[12]: Traceback (most recent call last):
2026-08-22T06:25:41+00:00 bert gunicorn[12]:   File "x.py", line 1, in y
2026-08-22T06:25:41+00:00 bert gunicorn[12]: django.db.utils.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
2026-08-22T06:25:41+00:00 bert gunicorn[12]:         Is the server running on that host and accepting TCP/IP connections?
2026-08-22T06:26:00+00:00 bert gunicorn[11]: Internal Server Error: /bios/billy-dunlop/games/
2026-08-22T06:26:00+00:00 bert gunicorn[11]: Traceback (most recent call last):
2026-08-22T06:26:00+00:00 bert gunicorn[11]: AttributeError: 'NoneType' object has no attribute 'games_played'
2026-08-29T01:55:46+00:00 bert gunicorn[1]: [2026-08-29 01:55:46 +0000] [1] [CRITICAL] WORKER TIMEOUT (pid:13)
2026-08-29T01:55:46+00:00 bert gunicorn[13]: [2026-08-28 20:55:46 -0500] [13] [ERROR] Error handling request GET /sources/24/
2026-08-29T01:55:46+00:00 bert gunicorn[13]: Traceback (most recent call last):
2026-08-29T01:55:46+00:00 bert gunicorn[13]:     sys.exit(1)
2026-08-29T01:55:46+00:00 bert gunicorn[13]: SystemExit: 1
2026-08-29T01:55:47+00:00 bert gunicorn[14]: [2026-08-29 01:55:47 +0000] [14] [INFO] Booting worker with pid: 14
"""


class ErrorDigestTests(SimpleTestCase):

    def test_pairs_errors_with_their_exception_across_interleaved_workers(self):
        errors, timeouts = parse(JOURNAL.splitlines())
        self.assertEqual(
            errors["AttributeError: 'NoneType' object has no attribute 'games_played'"],
            {'/bios/jimmy-drain/': 1, '/bios/billy-dunlop/games/': 1})
        self.assertEqual(
            list(errors['django.db.utils.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused']),
            ['/places/cities/'])
        self.assertEqual(len(errors), 2)

    def test_timeouts_counted_by_path_and_not_as_500s(self):
        errors, timeouts = parse(JOURNAL.splitlines())
        self.assertEqual(timeouts, {'/sources/24/': 1})
        self.assertNotIn('SystemExit: 1', errors)

    def test_empty_journal(self):
        self.assertEqual(parse(['2026-08-29T01:55:47+00:00 bert gunicorn[14]: [INFO] Booting worker']), ({}, {}))

    def test_format(self):
        errors, timeouts = parse(JOURNAL.splitlines())
        text = format_digest(errors, timeouts, '24h')
        self.assertTrue(text.startswith('s2 errors, last 24h: 3 500s, 1 worker timeouts'))
        self.assertIn("   2  AttributeError: 'NoneType'", text)
        self.assertIn('         1  /sources/24/', text)


class SearchTests(SimpleTestCase):

    @patch('games.views.render')
    def test_uses_accent_insensitive_name_matching(self, render):
        request = RequestFactory().get('/search/', {'q': 'Pele'})

        search(request)

        context = render.call_args.args[2]
        self.assertIn('UNACCENT(', str(context['players'].query))
        self.assertIn('UNACCENT(', str(context['teams'].query))
        self.assertIn('UNACCENT(', str(context['competitions'].query))


class HomepageOnThisDayTests(SimpleTestCase):

    def test_places_single_item_history_strip_above_search(self):
        team1 = SimpleNamespace(name='Home', slug='home')
        team2 = SimpleNamespace(name='Away', slug='away')
        competition = SimpleNamespace(name='Major League Soccer', abbreviation='MLS')
        game = SimpleNamespace(
            id=7,
            date=datetime.date(1996, 9, 6),
            team1=team1,
            team2=team2,
            team1_original_name='Home',
            team2_original_name='Away',
            winner=team1,
            score_or_result='2 - 1',
            competition=competition,
        )
        born = SimpleNamespace(
            name='Player Name',
            slug='player-name',
            birthdate=datetime.date(1984, 9, 6),
        )

        html = render_to_string('homepage.html', {
            'today': datetime.date(2026, 9, 6),
            'oldest': game,
            'crowd': None,
            'born': born,
        })

        self.assertLess(html.index('id="otd"'), html.index('id="home-search"'))
        self.assertEqual(html.count('class="otd-item"'), 2)
        self.assertIn('class="otd-prev"', html)
        self.assertIn('class="otd-next"', html)
        self.assertIn('Earliest match', html)
        self.assertIn('Player Name was born', html)


class RecentResultsChartTests(SimpleTestCase):

    def test_builds_signed_bars_for_wins_losses_and_draws(self):
        team = SimpleNamespace(id=1)
        opponent = SimpleNamespace(name='Austin FC')
        games = [
            SimpleNamespace(id=1, date=datetime.date(2026, 8, 1),
                            team1_id=1, team1=team, team2=opponent,
                            team1_score=3, team2_score=1,
                            team1_result='w', team2_result='l'),
            SimpleNamespace(id=2, date=datetime.date(2026, 8, 8),
                            team1_id=2, team1=opponent, team2=team,
                            team1_score=4, team2_score=1,
                            team1_result='w', team2_result='l'),
            SimpleNamespace(id=3, date=datetime.date(2026, 8, 15),
                            team1_id=1, team1=team, team2=opponent,
                            team1_score=2, team2_score=2,
                            team1_result='t', team2_result='t'),
        ]

        chart = recent_results_chart(team, games)

        self.assertEqual([bar['result'] for bar in chart['bars']],
                         ['win', 'loss', 'tie'])
        self.assertEqual([bar['value'] for bar in chart['bars']],
                         ['+2', '\N{MINUS SIGN}3', '0'])
        self.assertLess(chart['bars'][0]['y'], chart['svg']['baseline'])
        self.assertEqual(chart['bars'][1]['y'], chart['svg']['baseline'])
        html = render_to_string('templatetags/charts/results.html', chart)
        self.assertIn('class="mark win"', html)
        self.assertIn('class="mark loss"', html)
        self.assertIn('class="mark tie"', html)
