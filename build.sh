#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
cd charmaway/
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py flush --no-input
python seed_all.py