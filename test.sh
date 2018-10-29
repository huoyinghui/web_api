#!/usr/bin/env bash

# pip install when-changed
 when-changed -v -r -1 -s ./    "python manage.py test rest_learn"
