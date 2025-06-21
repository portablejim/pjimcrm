#!/bin/bash

git pull
../venv/bin/python manage.py collectstatic
systemctl reload apache2
