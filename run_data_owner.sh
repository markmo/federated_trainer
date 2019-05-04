#!/usr/bin/env bash

export PYTHONPATH=.

gunicorn -b "0.0.0.0:5000" --chdir data_owner wsgi:app --preload