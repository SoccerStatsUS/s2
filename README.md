### An open source, logical soccer database

This is the code used to create an integrated, reasonably maintained soccer database, with an ORM layer including models and views written in Django (5.2, Python 3.12).

The site is served at soccerstats.us (stats.soccerstats.us and www 301 to it as of 2026-08-02).

#### Local setup

    # postgres (e.g. brew install postgresql@18) with a soccerstats role:
    psql -d postgres -c "CREATE ROLE soccerstats LOGIN CREATEDB"

    cd ~/soccer/s2
    uv venv --python 3.12
    uv pip install -p .venv/bin/python -r requirements3.txt

    # Build the mongo database first (see the build repo), then:
    ./build.sh              # mongo -> postgres (soccerstats_dev)

    .venv/bin/python manage.py runserver

Settings are env-driven (see settings.py): DJANGO_SECRET_KEY, DJANGO_DEBUG,
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST. Local defaults work with a trusting
local postgres and DEBUG on.

#### Deploy

Production runs on the server "bert" at /home/chris/www/s2:

* gunicorn via systemd (etc/systemd/s2.service), bound to 127.0.0.1:8100
* nginx proxies soccerstats.us to it (etc/nginx/soccerstats.us);
  etc/nginx/stats.soccerstats.us is now just the 301 to the apex
* AI crawlers (ClaudeBot, GPTBot) are rate-limited to 10 req/min per IP —
  zone in etc/nginx/conf.d/ai-bot-ratelimit.conf, applied in the vhost's
  `location /`, which also serves a robots.txt with a Crawl-delay hint.
  They were doing ~84k req/day combined before this (2026-08-02).
  That limit only reaches crawlers that identify themselves; scraper farms
  spoofing browser user-agents are blocked by network instead, in
  etc/nginx/conf.d/blocked-networks.conf.
* secrets live in /home/chris/www/s2/.env (not in git)

The files under etc/ are the source of truth, but nothing syncs them — bert
holds copies. After changing one, deploy it:

    ssh bert 'cd /home/chris/www/s2 && git pull && \
        sudo cp etc/nginx/conf.d/*.conf /etc/nginx/conf.d/ && \
        sudo cp etc/nginx/soccerstats.us etc/nginx/stats.soccerstats.us \
            /etc/nginx/sites-available/ && \
        sudo nginx -t && sudo systemctl reload nginx'

Certbot edits the live vhosts in place, so copy the live file back into the
repo after any cert change or the next deploy reverts it.

Before deploying, smoke-test every major URL pattern against the local db:

    .venv/bin/python manage.py smoketest

To deploy code changes:

    ssh bert 'cd /home/chris/www/s2 && git pull && \
        set -a && . ./.env && set +a && \
        .venv/bin/python manage.py migrate --noinput && \
        .venv/bin/python manage.py collectstatic --noinput && \
        chmod -R a+rX staticfiles && sudo systemctl restart s2'

Sourcing .env is not optional: without it manage.py falls back to settings.py's
dev defaults and migrate fails on Postgres peer auth as "soccerstats".

To ship a freshly built database:

    ./upload.sh

#### Errors

Request errors go to stderr, so `journalctl -u s2` on bert has every 500 with
its traceback. `etc/systemd/s2-errordigest.timer` runs `manage.py errordigest`
each morning to summarize the last day's 500s and worker timeouts by exception
and path; it is silent when there were none. Until EMAIL_HOST_PASSWORD is in
.env the digest prints instead of mailing, so read it with
`journalctl -u s2-errordigest`. To install or update the timer:

    ssh bert 'cd /home/chris/www/s2 && git pull && \
        sudo cp etc/systemd/s2-errordigest.* /etc/systemd/system/ && \
        sudo systemctl daemon-reload && \
        sudo systemctl enable --now s2-errordigest.timer'

To look further back, or at a saved dump:

    .venv/bin/python manage.py errordigest --since 7d
    .venv/bin/python manage.py errordigest --file journal.txt

#### Dependencies

soccerstatsus/build (mongo database), soccerstatsus/metadata, soccerstatsus/parse, and the data repositories.
