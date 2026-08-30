"""
Summarize the 500s and worker timeouts in the s2 journal, grouped by exception
and path. Meant to run daily from etc/systemd/s2-errordigest.timer; when there
is nothing to report it says nothing. Mails ADMINS if EMAIL_HOST_PASSWORD is
set, otherwise prints (which lands in the timer's own journal).

    .venv/bin/python manage.py errordigest              # last 24 hours
    .venv/bin/python manage.py errordigest --since 7d
    .venv/bin/python manage.py errordigest --file j.txt # a saved journalctl dump
"""

import re
import subprocess
from collections import Counter, defaultdict

from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand

LINE_RE = re.compile(r'^\S+ \S+ gunicorn\[(?P<pid>\d+)\]: (?P<msg>.*)$')
ERROR_RE = re.compile(r'^Internal Server Error: (?P<path>\S+)')
TIMEOUT_RE = re.compile(r'\[ERROR\] Error handling request (?:GET|POST|HEAD) (?P<path>\S+)')


def parse(lines):
    """
    Pair each "Internal Server Error: <path>" with the exception line of the
    traceback that follows it from the same worker. Returns
    ({exception: Counter(path)}, Counter(timeout path)).
    """
    errors = defaultdict(Counter)
    timeouts = Counter()
    pending = {}  # pid -> path awaiting its exception line

    for line in lines:
        m = LINE_RE.match(line.rstrip('\n'))
        if not m:
            continue
        pid, msg = m.group('pid'), m.group('msg')

        e = ERROR_RE.match(msg)
        if e:
            pending[pid] = e.group('path')
            continue

        t = TIMEOUT_RE.search(msg)
        if t:
            timeouts[t.group('path')] += 1
            pending.pop(pid, None)
            continue

        if pid in pending and msg and not msg[0].isspace() and not msg.startswith('Traceback'):
            errors[msg][pending.pop(pid)] += 1

    return errors, timeouts


def format_digest(errors, timeouts, since):
    n500 = sum(sum(c.values()) for c in errors.values())
    ntimeout = sum(timeouts.values())
    out = ['s2 errors, last %s: %d 500s, %d worker timeouts' % (since, n500, ntimeout), '']

    for exc, paths in sorted(errors.items(), key=lambda kv: -sum(kv[1].values())):
        out.append('%4d  %s' % (sum(paths.values()), exc[:200]))
        for path, n in paths.most_common(10):
            out.append('      %4d  %s' % (n, path))
        if len(paths) > 10:
            out.append('            ... %d more paths' % (len(paths) - 10))
        out.append('')

    if timeouts:
        out.append('%4d  worker timeouts' % ntimeout)
        for path, n in timeouts.most_common(10):
            out.append('      %4d  %s' % (n, path))
        out.append('')

    return '\n'.join(out)


class Command(BaseCommand):
    help = "Summarize 500s and worker timeouts from the s2 journal."

    def add_arguments(self, parser):
        parser.add_argument('--since', default='24h', help='journalctl --since span (default 24h)')
        parser.add_argument('--file', help='read a saved journalctl dump instead of running journalctl')

    def handle(self, *args, **options):
        since = options['since']
        if options['file']:
            with open(options['file']) as f:
                lines = f.readlines()
        else:
            result = subprocess.run(
                ['journalctl', '-u', 's2', '--since', '-' + since, '-o', 'short-iso', '--no-pager', '-q'],
                capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()

        errors, timeouts = parse(lines)
        if not errors and not timeouts:
            return

        body = format_digest(errors, timeouts, since)
        if settings.EMAIL_HOST_PASSWORD:
            mail_admins('s2 errors, last %s' % since, body)
        else:
            self.stdout.write(body)
