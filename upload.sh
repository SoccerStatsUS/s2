#!/bin/sh
# Ship the locally built database to production (bert) and restart the site.
set -e

DUMP=/tmp/soccerstats.dump

pg_dump -Fc -U soccerstats soccerstats_dev > $DUMP
scp $DUMP bert:/tmp/
rm $DUMP

ssh bert 'set -e
sudo -u postgres dropdb soccerstats
sudo -u postgres createdb soccerstats --owner=soccerstats
export PGPASSWORD=$(grep DB_PASSWORD /home/chris/www/s2/.env | cut -d= -f2)
pg_restore -h 127.0.0.1 -U soccerstats -d soccerstats --no-owner /tmp/soccerstats.dump
rm /tmp/soccerstats.dump
sudo systemctl restart s2'

echo "Shipped to bert."
