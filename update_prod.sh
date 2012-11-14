export PGPASSWORD=ymctas

dropdb soccerstats
psql -U soccerstats -d soccerstats_backup -c "CREATE DATABASE soccerstats WITH TEMPLATE soccerstats_dev"

sudo stop s2prod
sudo start s2prod
sudo /etc/init.d/memcached restart