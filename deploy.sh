#!/bin/bash
# Full rebuild-and-ship: data repos -> mongo -> postgres -> bert, then code.
# Runs build/build.sh, then this repo's build.sh, then upload.sh, then pushes
# master and deploys it on bert, in order, stopping at the first failure.
set -e
cd "$(dirname "$0")"

../build/build.sh
./build.sh
./upload.sh

git push origin master
ssh bert 'cd /home/chris/www/s2 && git pull && \
    set -a && . ./.env && set +a && \
    .venv/bin/python manage.py migrate --noinput && \
    .venv/bin/python manage.py collectstatic --noinput && \
    chmod -R a+rX staticfiles && sudo systemctl restart s2'
echo "Code deployed to bert."
