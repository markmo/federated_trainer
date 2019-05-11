#!/usr/bin/env bash

export PYTHONPATH=.

gunicorn -b "0.0.0.0:9000" --chdir data_owners wsgi:app --preload