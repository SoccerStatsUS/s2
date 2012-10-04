
source ~/.virtualenvs/sdev/bin/activate



# Need to check that this exists first.
#cp db/soccer.db db/backup.soccer.db
#cp db/soccer.build.db db/soccer.db
#sudo su postgres
#exit

dropdb soccerstats
createdb -T template_postgis soccerstats --owner=soccerstats
python manage.py syncdb --no
python build/
python build/generate.py
python manage.py rebuild_index --noinput

