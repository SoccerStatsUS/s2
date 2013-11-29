pg_dump soccerstats_dev > tmp.sql
scp tmp.sql bert:/home/chris/www/sdev
rm -f tmp.sql