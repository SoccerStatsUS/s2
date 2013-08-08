export PGPASSWORD=ymctas

read -p "dropping soccerstats db - are you sure?" -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "rpdating db"
  dropdb soccerstats
  psql -U soccerstats -d soccerstats_dev -c "CREATE DATABASE soccerstats WITH TEMPLATE soccerstats_dev"

  echo "restarting site"
  sudo stop s2prod
  sudo start s2prod
  sudo /etc/init.d/memcached restart

  python manage.py rebuild_index
fi