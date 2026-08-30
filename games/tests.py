from django.test import SimpleTestCase

from games.management.commands.errordigest import format_digest, parse

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
