### An open source, logical soccer database

This is the code used to create an integrated, reasonably maintained soccer database, with an ORM layer including models and views written in Django (5.2, Python 3.12).

The site is served at stats.soccerstats.us; the static landing page lives in the soccerstats.us repository.

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
* nginx proxies stats.soccerstats.us to it (etc/nginx/stats.soccerstats.us)
* secrets live in /home/chris/www/s2/.env (not in git)

To deploy code changes:

    ssh bert 'cd /home/chris/www/s2 && git pull && \
        .venv/bin/python manage.py migrate --noinput && \
        .venv/bin/python manage.py collectstatic --noinput && \
        chmod -R a+rX staticfiles && sudo systemctl restart s2'

To ship a freshly built database:

    ./upload.sh

#### Dependencies

soccerstatsus/build (mongo database), soccerstatsus/metadata, soccerstatsus/parse, and the data repositories.
