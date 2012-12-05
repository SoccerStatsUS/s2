export PGPASSWORD=ymctas

sudo echo "working"

dropdb soccerstats
psql -U soccerstats -d soccerstats_dev -c "CREATE DATABASE soccerstats WITH TEMPLATE soccerstats_dev"

sudo stop s2prod
sudo start s2prod
sudo /etc/init.d/memcached restart