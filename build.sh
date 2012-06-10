
source ~/.virtualenvs/sdev/bin/activate

python build/

# Need to check that this exists first.
cp db/soccer.db db/backup.soccer.db
cp db/soccer.build.db db/soccer.db

python build/generate.py
python manage.py rebuild_index --noinput

