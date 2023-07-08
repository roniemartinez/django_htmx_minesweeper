#!/bin/bash

if [[ "${DEBUG}" == "true" ]]; then
  python manage.py runserver 0.0.0.0:8080
else
  daphne -b 0.0.0.0 -p 8080 django_htmx_minesweeper.asgi:application
fi
