#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


python /app/manage.py collectstatic --noinput
/usr/local/bin/gunicorn gamebook.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app