#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requipment.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate