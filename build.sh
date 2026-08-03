#!/bin/bash
# Rebuild the local postgres database from the mongo database.
# Run from the s2 directory after a `../build/build.sh` build.
# Writes everything to logs/build.log as well as the terminal.
set -e
cd "$(dirname "$0")"

mkdir -p logs
LOG=logs/build.log
exec > >(tee "$LOG") 2>&1

echo "build started $(date)"

dropdb --if-exists soccerstats_build
createdb soccerstats_build --owner=soccerstats

.venv/bin/python manage.py migrate --noinput --settings=build_settings
PYTHONPATH=$PWD .venv/bin/python build/load.py 1
PYTHONPATH=$PWD .venv/bin/python build/load.py 2
PYTHONPATH=$PWD .venv/bin/python build/load.py 3
PYTHONPATH=$PWD .venv/bin/python build/load.py 4
PYTHONPATH=$PWD .venv/bin/python build/generate.py

dropdb --if-exists soccerstats_backup
psql -d postgres -c 'ALTER DATABASE soccerstats_dev RENAME TO soccerstats_backup' || true
psql -d postgres -c 'ALTER DATABASE soccerstats_build RENAME TO soccerstats_dev'

echo "soccerstats_dev rebuilt (previous version saved as soccerstats_backup)."

echo
echo "--- teams created because no name/short_name matched, deduped ---"
grep '^Creating team ' "$LOG" | sort | uniq -c | sort -rn || echo "none"
