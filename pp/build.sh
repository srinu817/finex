#!/usr/bin/env bash
set -o errexit

cd ..

pip install -r pp/requirements.txt

cd pp

python manage.py collectstatic --noinput
python manage.py migrate