dropdb soccerstats
psql -U soccerstats -d soccerstats_backup -c "CREATE DATABASE soccerstats WITH TEMPLATE soccerstats_dev"

