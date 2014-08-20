
export PGPASSWORD=ymctas

# Need separate script for moving to prod?
#source ~/.virtualenvs/sdev/bin/activate

dropdb soccerstats_build
createdb soccerstats_build --owner=soccerstats
createdb soccerstats_backup --owner=soccerstats
createdb soccerstats --owner=soccerstats
python manage.py syncdb --noinput --settings=build_settings
python build/load.py 1
python build/load.py 2
python build/load.py 3
python build/load.py 4
python build/generate.py

dropdb soccerstats_backup
psql -U soccerstats -d soccerstats_build -c "ALTER DATABASE soccerstats_dev RENAME TO soccerstats_backup"
psql -U soccerstats -d soccerstats_backup -c "ALTER DATABASE soccerstats_build RENAME TO soccerstats_dev"
