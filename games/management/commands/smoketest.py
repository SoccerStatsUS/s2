"""
Hit every major URL pattern with real data from the current database and
report anything that returns a 500. Run before deploying:

    .venv/bin/python manage.py smoketest
"""

from django.core.management.base import BaseCommand
from django.test import Client


# Routes that exist but whose pages aren't built yet (see /more/). They are
# expected to error until built; the smoke test reports but tolerates them.
UNBUILT = {
    '/games/',
    '/news/',
    '/organizations/',
    '/places/states/',
    '/places/cities/',
    '/places/stadiums/',
    '/positions/',
    '/stats/',
}

# Unlinked, half-built detail routes: nothing links to them and their
# views/templates were never finished.
def is_unbuilt(url):
    if url in UNBUILT:
        return True
    if url.startswith('/bios/') and url.endswith(('/goals/', '/stats/')):
        return True
    if url.startswith('/c/') and url.endswith('/salaries/'):
        return True
    if url.startswith('/teams/') and url.count('/') == 5 and url.split('/')[3] == 'c':
        return True
    return False


class Command(BaseCommand):
    help = "GET every major URL pattern with real data; fail on any 500."

    def handle(self, *args, **options):
        from awards.models import Award
        from bios.models import Bio
        from competitions.models import Competition, Season
        from drafts.models import Draft
        from games.models import Game
        from places.models import City, Country, Stadium, State
        from sources.models import Source
        from teams.models import Team

        def first(qs):
            try:
                return qs[0]
            except IndexError:
                return None

        bio = first(Bio.objects.filter(slug='landon-donovan')) or first(Bio.objects.exclude(slug=''))
        ref = first(Bio.objects.exclude(games_refereed=None).distinct())
        competition = first(Competition.objects.filter(slug='major-league-soccer')) or first(Competition.objects.all())
        season = first(Season.objects.filter(competition=competition).order_by('-name'))
        team = first(Team.objects.filter(slug='chicago-fire')) or first(Team.objects.all())
        team2 = first(Team.objects.filter(slug='la-galaxy')) or first(Team.objects.exclude(id=team.id if team else None))
        game = first(Game.objects.exclude(date=None).order_by('-date'))
        award = first(Award.objects.all())
        source = first(Source.objects.exclude(games=None).order_by('-games'))
        draft = first(Draft.objects.exclude(competition=None))
        stadium = first(Stadium.objects.exclude(slug=''))
        city = first(City.objects.exclude(slug=''))
        state = first(State.objects.exclude(slug=''))
        country = first(Country.objects.filter(slug='usa')) or first(Country.objects.exclude(slug=''))

        urls = [
            '/',
            '/search/?q=donovan',
            '/more/',
            '/about/',
            '/about/news/',
            '/about/build/',
            '/awards/',
            '/bios/',
            '/c/',
            '/dates/',
            '/drafts/',
            '/games/',
            '/news/',
            '/organizations/',
            '/organizations/confederations/',
            '/places/',
            '/places/states/',
            '/places/cities/',
            '/places/stadiums/',
            '/positions/',
            '/sources/',
            '/stats/',
            '/teams/',
        ]

        if award:
            urls.append('/awards/%s/' % award.id)

        if bio:
            urls += [
                '/bios/%s/' % bio.slug,
                '/bios/%s/games/' % bio.slug,
                '/bios/%s/goals/' % bio.slug,
                '/bios/%s/stats/' % bio.slug,
                '/bios/id/%s/' % bio.id,
            ]

        if ref:
            urls.append('/bios/%s/referee/' % ref.slug)

        if competition:
            urls += [
                '/c/%s/' % competition.slug,
                '/c/%s/stats/' % competition.slug,
                '/c/%s/games/' % competition.slug,
                '/c/%s/attendance/' % competition.slug,
            ]

        if season:
            base = '/c/%s/%s/' % (competition.slug, season.slug)
            urls += [base] + [base + suffix for suffix in
                              ('stats/', 'games/', 'goals/', 'attendance/', 'salaries/')]

        if game and game.date:
            urls += [
                '/games/%s/' % game.id,
                '/dates/%s/' % game.date.year,
                '/dates/%s/%s/' % (game.date.year, game.date.month),
                '/dates/%s/%s/%s/' % (game.date.year, game.date.month, game.date.day),
                '/dates/day/%s/%s/' % (game.date.month, game.date.day),
            ]

        if draft:
            urls.append('/drafts/%s/%s/%s/' % (draft.competition.slug, draft.slug, draft.season.name))

        if source:
            urls.append('/sources/%s/' % source.id)

        if stadium:
            urls += ['/places/stadiums/%s/' % stadium.slug, '/places/stadiums/%s/games' % stadium.slug]
        if city:
            urls.append('/places/cities/%s/' % city.slug)
        if state:
            urls.append('/places/states/%s/' % state.slug)
        if country:
            urls.append('/places/countries/%s/' % country.slug)

        if team:
            urls += [
                '/teams/%s/' % team.slug,
                '/teams/%s/stats/' % team.slug,
                '/teams/%s/picks/' % team.slug,
                '/teams/%s/draftees/' % team.slug,
                '/teams/%s/games/' % team.slug,
            ]
            if game and game.date:
                urls.append('/teams/%s/%s/' % (team.slug, game.date.year))
            if team2:
                urls.append('/teams/%s/v/%s/' % (team.slug, team2.slug))
            if competition:
                urls.append('/teams/%s/c/%s/' % (team.slug, competition.slug))

        client = Client()
        failures = []
        unbuilt_seen = 0

        for url in urls:
            try:
                status = client.get(url, HTTP_HOST='localhost').status_code
            except Exception as e:
                status = '%s: %s' % (type(e).__name__, e)

            ok = isinstance(status, int) and status < 500
            if ok:
                style, note = self.style.SUCCESS, ''
            elif is_unbuilt(url):
                style, note = self.style.WARNING, ' (unbuilt, tolerated)'
                unbuilt_seen += 1
            else:
                style, note = self.style.ERROR, ''
                failures.append((url, status))
            self.stdout.write('%-60s %s%s' % (url, style(str(status)), note))

        self.stdout.write('')
        if failures:
            self.stdout.write(self.style.ERROR('%s of %s URLs failed:' % (len(failures), len(urls))))
            for url, status in failures:
                self.stdout.write(self.style.ERROR('  %s -> %s' % (url, status)))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(
            'All %s URLs OK (%s unbuilt tolerated).' % (len(urls), unbuilt_seen)))
